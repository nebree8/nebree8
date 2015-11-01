"""Polls the AppEngine frontend for recipes compile.

When a recipe is found, the actions for it are pushed to the controller if
the controller has no pending actions.
"""

import json
import logging
import time
import threading
import urllib
import urllib2

from actions.action import Action
from drinks import random_drinks
from drinks.recipe import Recipe
from server import actions_for_recipe, recipe_from_json_object

class UpdateProgressAction(Action):
    def __init__(self, syncer, key, percent):
        self.syncer = syncer
        self.key = key
        self.percent = percent

    def __call__(self, robot):
        self.syncer.post("set_drink_progress", key=self.key, progress=self.percent)


class DummyApp: pass

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
                        continue  # Don't make the same drink twice
                    last_drink_id = drink_id
                    next_recipe = recipe_from_json_object(json_recipe)
                    print "Queueing Recipe: %s" % next_recipe
                    actions = actions_for_recipe(next_recipe)
                    actions.insert(0, UpdateProgressAction(self, drink_id, 10))
                    actions.append(FinishDrinkAction(self, drink_id))
                    self.controller.EnqueueGroup(actions)
                else:
                    actions = self.controller.InspectQueue()
                    if actions:
                        print "Current action: ", actions[0].inspect()
                        if actions[0].__class__.__name__ == 'WaitForGlassPlaced' and self.controller.robot.__class__.__name__ == 'FakeRobot':
                            print "Placing glass"
                            actions[0].force = True
                self.write(queue)
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
