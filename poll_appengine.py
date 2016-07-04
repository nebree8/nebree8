"""Polls the AppEngine frontend for orders.

When a recipe is found, the actions for it are pushed to the controller if
the controller has no pending actions.
"""

import json
import logging
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


class UpdateProgressAction(Action):
  def __init__(self, syncer, key, percent):
    self.syncer = syncer
    self.key = key
    self.percent = percent

  def __call__(self, robot):
    self.syncer.post("set_drink_progress", key=self.key, progress=self.percent)


class DummyApp(object):
  pass


class FinishDrinkAction(Action):
  def __init__(self, syncer, key):
    self.syncer = syncer
    self.key = key

  def __call__(self, robot):
    self.syncer.post("finished_drink", key=self.key)


class SyncToServer(threading.Thread):
  """Polls nebree8.com for recipes to make."""

  def __init__(self, base_url, poll_frequency_secs, controller):
    super(self.__class__, self).__init__()
    self.queuefile = 'remote_queue.txt'
    self.base_url = base_url
    self.poll_frequency_secs = poll_frequency_secs
    self.controller = controller
    self.daemon = True
    if FLAGS.check_ingredients:
      config = json.loads(self.get('get_config'))
      logging.info("Frontend config=%s", config)
      backend_ingredients = set(
          i for i in ingredients.IngredientsOrdered()
          if i not in ("air", "") and not i.endswith("_backup"))
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

  def get(self, url):
    return urllib2.urlopen(self.base_url + url).read()

  def post(self, url, **kwargs):
    try:
      url = self.base_url + url
      data = urllib.urlencode(kwargs)
      print "POST %s %s" % (url, data)
      return urllib2.urlopen(url=url, data=data).read()
    except urllib2.HTTPError, e:
      print e
      raise

  def run(self):
    last_drink_id = None
    while True:
      try:
        queue = json.loads(self.get('next_drink'))
        if not self.controller and queue:
          json_recipe = queue[0]
          drink_id = json_recipe['id']
          if drink_id == last_drink_id:
            print "Refusing to remake order %s" % last_drink_id
            time.sleep(20)   # Sleep extra long
            continue  # Don't make the same drink twice
          last_drink_id = drink_id
          next_recipe = water_down_recipe(Recipe.from_json(json_recipe))
          print "Queueing Recipe in 5 seconds: %s" % next_recipe
          time.sleep(5)
          raw_actions = actions_for_recipe(next_recipe)
          actions = []
          for i, action in enumerate(raw_actions):
            progress = 10 + 90 * i / len(raw_actions)
            actions.append(UpdateProgressAction(self, drink_id, progress))
            actions.append(action)
          actions.append(FinishDrinkAction(self, drink_id))
          self.controller.EnqueueGroup(actions)
        else:
          actions = self.controller.InspectQueue()
          if actions:
            print "Current action: ", actions[0].inspect()
            if (isinstance(actions[0],
                           (WaitForGlassRemoval, WaitForGlassPlaced)) and
                isinstance(self.controller.robot, FakeRobot)):
              print "Placing glass"
              actions[0].force = True
        self.write(queue)
      except urllib2.URLError, e:
        logging.warning("URLError: %s", e)
      except ValueError, e:
        print e
      time.sleep(self.poll_frequency_secs)

  def write(self, queue):
    with open(self.queuefile, 'w') as f:
      for order in queue or []:
        recipe = Recipe.from_json(order)
        f.write(str(recipe))


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
