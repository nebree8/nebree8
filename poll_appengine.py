"""Polls the AppEngine frontend for orders.

When a recipe is found, the actions for it are pushed to the controller if
the controller has no pending actions.
"""

import contextlib
import json
import logging
import socket
import time
import threading
import urllib
import urllib2

import gflags

from actions.action import Action
from actions.wait_for_glass_placed import WaitForGlassPlaced
from actions.wait_for_glass_removal import WaitForGlassRemoval
from config import ingredients
from drinks.actions_for_recipe import actions_for_recipe
from drinks.recipe import Recipe
from drinks.water_down import water_down_recipe
from fake_robot import FakeRobot

FLAGS = gflags.FLAGS
gflags.DEFINE_bool("check_ingredients", True,
                   "Cross check list of ingredients with INGREDIENTS_ORDERED")
gflags.DEFINE_integer("urllib_timeout_secs", 1,
                      "Timeout in secs for GET and POSTs")


class UpdateProgressAction(Action):
  def __init__(self, syncer, key, percent):
    self.syncer = syncer
    self.key = key
    self.percent = percent

  def __call__(self, robot):
    try:
      self.syncer.post("set_drink_progress",
                       attempts=1,
                       key=self.key,
                       progress=self.percent)
    except (urllib2.URLError, socket.timeout) as e:
      logging.warning("set_drink_progress failed: %s", e)

  def __str__(self):
    if self.syncer.current_drink:
      self.syncer.current_drink['progress_percent'] = self.percent
    return 'UpdateProgressAction: key=...%s percent=%s' % (self.key[-10:],
                                                           self.percent)


class DummyApp(object):
  pass


class FinishDrinkAction(Action):
  def __init__(self, syncer, drink):
    self.syncer = syncer
    self.drink = drink

  def __call__(self, robot):
    self.syncer.post("finished_drink", key=self.drink['id'])
    self.syncer.finished_drink = self.drink
    self.syncer.current_drink = {}

class SyncToServer(threading.Thread):
  """Polls nebree8.com for recipes to make."""

  def __init__(self, base_url, poll_frequency_secs, controller):
    super(self.__class__, self).__init__()
    self.queuefile = 'remote_queue.txt'
    self.jsonqueuefile = 'static/order-queue.json'
    self.finished_drink = {}
    self.current_drink = {}
    self.base_url = base_url
    self.poll_frequency_secs = poll_frequency_secs
    self.controller = controller
    self.daemon = True
    if FLAGS.check_ingredients:
      print("checking ingredients")
      config = json.loads(self.get(url='get_config', attempts=3))
      logging.info("Frontend config=%s", config)
      backend_ingredients = (set(
          i for i in ingredients.IngredientsOrdered()
          if i not in ("air", "") and not i.endswith(ingredients.BACKUP)) |
                             set(ingredients.OVERRIDES.keys()))
      frontend_ingredients = set()
      for ingredient in config.get("Ingredients", []):
        name = ingredient.get('Name', '')
        if ingredient.get('Available', False) and name:
          frontend_ingredients.add(name)
      if backend_ingredients - frontend_ingredients:
        logging.error('Ingredients missing from frontend: %s',
                      ', '.join(backend_ingredients - frontend_ingredients))
      if frontend_ingredients - backend_ingredients:
        logging.error('Ingredients missing from backend: %s',
                      ', '.join(frontend_ingredients - backend_ingredients))
      if frontend_ingredients != backend_ingredients:
        raise NotImplementedError("Ingredients differ on backend and frontend. "
                                  + "Disable check with --nocheck_ingredients")

  def get(self, url, attempts=-1):
    return self._urlopen(url=self.base_url + url, attempts=attempts)

  def post(self, url, attempts=-1, **kwargs):
    return self._urlopen(url=self.base_url + url,
                         attempts=attempts,
                         data=urllib.urlencode(kwargs))

  @staticmethod
  def _urlopen(url, attempts, **kwargs):
    attempt = 1
    while True:
      try:
        timeout_factor = 5 if attempts <= 1 else attempts
        with contextlib.closing(urllib2.urlopen(
            url=url, timeout=FLAGS.urllib_timeout_secs * timeout_factor,
            **kwargs)) as f:
          return f.read()
      except (urllib2.URLError, urllib2.HTTPError, socket.timeout):
        if attempts <= 0:
          logging.exception("retrying urlopen(%s) indefinitely", url)
        elif attempt >= attempts:
          raise
        attempt += 1

  def run(self):
    while True:
      try:
        queue = json.loads(self.get(url='next_drink', attempts=1))
        if not self.controller and queue:
          json_recipe = queue[0]
          drink_id = json_recipe['id']
          if drink_id == self.finished_drink.get('id'):
            print "Refusing to remake order %s" % self.finished_drink['id']
            time.sleep(20)   # Sleep extra long
            continue  # Don't make the same drink twice
          self.current_drink = json_recipe
          next_recipe = water_down_recipe(Recipe.from_json(json_recipe))
          raw_actions = actions_for_recipe(next_recipe)
          actions = []
          for i, action in enumerate(raw_actions):
            progress = 10 + 90 * i / len(raw_actions)
            actions.append(UpdateProgressAction(self, drink_id, progress))
            actions.append(action)
          actions.append(FinishDrinkAction(self, self.current_drink))
          self.controller.EnqueueGroup(actions)
        else:
          actions = self.controller.InspectQueue()
          if actions:
            logging.info("Current action: %s", actions[0])
            if (isinstance(actions[0],
                           (WaitForGlassRemoval, WaitForGlassPlaced)) and
                isinstance(self.controller.robot, FakeRobot)):
              logging.info("Placing glass")
              actions[0].force = True
        self.write(queue)
      except (urllib2.URLError, urllib2.HTTPError, socket.timeout) as e:
        logging.warning("urllib error: %s", e)
      except ValueError, e:
        print e
      time.sleep(self.poll_frequency_secs)

  def write(self, queue):
    with open(self.queuefile, 'w') as f:
      for order in queue or []:
        recipe = Recipe.from_json(order)
        f.write(str(recipe))
    queue_for_display = {
      'finished_drink': self.finished_drink,
      'current_drink': self.current_drink,
      'queue': queue or []
    }
    with open(self.jsonqueuefile, 'w') as f:
      json.dump(queue_for_display, f)

def unittest():
  from controller import Controller
  from fake_robot import FakeRobot
  fake_robot = FakeRobot()
  controller = Controller(fake_robot)
  controller.app = DummyApp()
  syncer = SyncToServer('http://localhost:8080/api/', 5, controller)
  syncer.run()


if __name__ == "__main__":
  unittest()
