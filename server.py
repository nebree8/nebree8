#!/usr/bin/env python

import json
import logging
import socket
import sys
import time
import traceback

import gflags
import webapp2

from actions.compressor import CompressorToggle
from actions.compressor import State
from actions.dispense_cup import DispenseCup, ReleaseCup
from actions.home import Home
from actions.led import SetLedForValve
from actions.meter_bitters import MeterBitters
from actions.meter_simple import MeterSimple as Meter
from actions.move import Move
from actions.pressurize import HoldPressure, ReleasePressure
from config import ingredients
from config import valve_position
from controller import Controller
from drinks import manual_db
from drinks.actions_for_recipe import actions_for_recipe
from drinks.random_drinks import RandomSourDrink, RandomSpirituousDrink, RandomBubblySourDrink, RandomBubblySpirituousDrink
from drinks.recipe import Recipe
from drinks.water_down import water_down_recipe
from fake_robot import FakeRobot
import poll_appengine

FLAGS = gflags.FLAGS

TEMPLATE_DIR = "templates/"
STATIC_FILE_DIR = "static/"
robot = None
controller = None
CUP_DISPENSE_POSITION = -3.465


class CustomJsonEncoder(json.JSONEncoder):
  def default(self, obj):
    if (hasattr(obj, '__class__') and obj.__class__.__name__ in
        ('ActionException', 'LoadCellMonitor', 'TareTimeout', 'MeterTimeout')):
      key = '__%s__' % obj.__class__.__name__
      return {key: obj.__dict__}
    return json.JSONEncoder.default(self, obj)


def GetTemplate(filename):
  return open(TEMPLATE_DIR + filename).read()


def ServeFile(filename):
  class ServeFileImpl(webapp2.RequestHandler):
    def get(self):
      self.response.write(open(filename).read())

  return ServeFileImpl


class LoadCellJson(webapp2.RequestHandler):
  def get(self):
    self.response.write("[")
    self.response.write(','.join('[%s, %f]' % rec
                                 for rec in robot.load_cell.recent_secs(10)))
    self.response.write("]")


class DrinkDbHandler(webapp2.RequestHandler):
  def get(self):
    self.response.content_type = 'application/javascript'
    self.response.write("db = ['%s'];" % "','".join(r.name
                                                    for r in manual_db.db))


class InspectQueueJson(webapp2.RequestHandler):
  def get(self):
    """Displays the state of the action queue."""
    self.response.write(json.dumps({
        'actions': [action.inspect() for action in controller.InspectQueue()],
        'exception': controller.last_exception
    },
                                   cls=CustomJsonEncoder))


class InspectQueue(webapp2.RequestHandler):
  def get(self):
    """Displays the state of the action queue."""
    actions = controller.InspectQueue()
    content = []
    if not actions:
      content.append("Queue is empty")
    else:
      for action in actions:
        d = action.inspect()
        name, props = d['name'], d['args']
        content.append(name)
        for prop in props.items():
          content.append('\t%s: %s' % prop)
    self.response.write(GetTemplate('queue.html').format(
        exception=controller.last_exception,
        content='\n'.join(content),
        robot_dict=robot.__dict__))


META_REFRESH = """
<html>
  <head>
    <title>{msg}</title>
    <meta http-equiv="refresh" content="2;URL={url}">
  </head>
<body>
{msg}
</body>
</html>
"""


class RetryQueue(webapp2.RequestHandler):
  def post(self):
    if controller.last_exception:
      controller.Retry()
    self.response.write(META_REFRESH.format(msg="Retrying...", url="/queue"))


class ClearQueue(webapp2.RequestHandler):
  def post(self):
    controller.ClearAndResume()
    self.response.write(META_REFRESH.format(msg="Cleared...", url="/queue"))


class SkipQueue(webapp2.RequestHandler):
  def post(self):
    if controller.last_exception:
      controller.SkipAndResume()
    self.response.write(META_REFRESH.format(msg="Skipped...", url="/queue"))


class StaticFileHandler(webapp2.RequestHandler):
  """Serve static files out of STATIC_FILE_DIR."""

  def get(self):
    if '.svg' in self.request.path:
      self.response.content_type = 'application/svg+xml'
    elif '.png' in self.request.path:
      self.response.content_type = 'image/png'
    elif '.jpg' in self.request.path:
      self.response.content_type = 'image/jpg'
    elif '.js' in self.request.path:
      self.response.content_type = 'application/javascript'
    relative_path = self.to_relative_path(self.request.path)
    path = STATIC_FILE_DIR + relative_path
    try:
      logging.debug("%s => %s", self.request.path, path)
      self.response.write(open(path).read())
    except IOError:
      print "404 could not load: %s" % path
      self.response.status = 404

  def to_relative_path(self, path):
    if len(path) > 0 and path[0] == "/":
      return path[1:]


def SingleActionHandler(action):
  """Create a handler for queueing the given action class"""

  class Handler(webapp2.RequestHandler):
    def post(self):
      controller.EnqueueGroup([action(),])
      self.response.write("%s action queued." % action.__name__)

  return Handler


def recipe_from_json_object(recipe_obj):
  """Takes a dict decoded from a JSON recipe and returns a Recipe object."""
  recipe = Recipe.from_json(recipe_obj)
  if not recipe.ingredients:
    if recipe_obj['drink_name'] == "Random Sour":
      recipe = RandomSourDrink()
      recipe.user_name = recipe_obj['user_name']
    elif recipe_obj['drink_name'] == "Random Boozy":
      recipe = RandomSpirituousDrink()
      recipe.user_name = recipe_obj['user_name']
    elif recipe_obj['drink_name'] == "Random Bubbly Boozy":
      recipe = RandomBubblySpirituousDrink()
      recipe.user_name = recipe_obj['user_name']
    elif recipe_obj['drink_name'] == "Random Bubbly Sour":
      recipe = RandomBubblySourDrink()
      recipe.user_name = recipe_obj['user_name']
  recipe = water_down_recipe(recipe)
  return recipe


class AllDrinksHandler(webapp2.RequestHandler):
  def get(self):
    drinks = []
    for drink in manual_db.LiveDB():
      data = drink.json
      data['image'] = drink.name.replace(' ', '_').lower() + '.jpg'
      drinks.append(data)
    self.response.write(json.dumps(drinks))
    print "responding to drinks request"


class DrinkHandler(webapp2.RequestHandler):
  def post(self):
    name = self.request.get('name')
    if name:
      for drink in manual_db.db:
        if drink.name.lower() == name.lower():
          self.response.write("Making drink %s" % drink)
          controller.EnqueueGroup(actions_for_recipe(drink))
          return
    elif self.request.get('random') == 'bubbly sour':
      controller.EnqueueGroup(actions_for_recipe(RandomBubblySourDrink()))
    elif self.request.get('random') == 'bubbly boozy':
      controller.EnqueueGroup(actions_for_recipe(RandomBubblySpirituousDrink()))
    elif self.request.get('random') == 'sour':
      controller.EnqueueGroup(actions_for_recipe(RandomSourDrink()))
    elif self.request.get('random') == 'boozy':
      controller.EnqueueGroup(actions_for_recipe(RandomSpirituousDrink()))
    self.response.status = 400


class PrimeHandler(webapp2.RequestHandler):
  def post(self):
    controller.EnqueueGroup(actions_for_recipe(manual_db.Recipe(
        name='Prime',
        ingredients=[
            manual_db.Ingredient(
                manual_db.Oz(.725), ingredient)
            for ingredient in ingredients.IngredientsOrdered()[:15]
            if ingredient != "air"
        ],
        #for ingredient in ingredients.IngredientsOrdered() if "itters" in ingredient],
        user_name="dev console")))


class FlushHandler(webapp2.RequestHandler):
  def post(self):
    flush_ingredients = [
        manual_db.Ingredient(
            manual_db.Oz(.725), ingredient)
        for ingredient in ingredients.IngredientsOrdered()
        if ingredient != "air"
    ]

    actions = []
    sorted_ingredients = sorted(
        flush_ingredients,
        key=lambda i: ingredients.IngredientNameToValvePosition(i.name, "Flush"))
    for ingredient in sorted_ingredients:
      valve = ingredients.IngredientNameToValvePosition(ingredient.name,
                                                        "Flush")
      actions.append(SetLedForValve(valve, 255, 0, 0))
    for ingredient in sorted_ingredients:
      valve = ingredients.IngredientNameToValvePosition(ingredient.name,
                                                        "Flush")
      actions.append(Move(valve_position(valve)))
      actions.append(SetLedForValve(valve, 0, 255, 0))
      actions.append(MeterBitters(valve_to_actuate=valve,
                                  drops_to_meter=20))
      actions.append(SetLedForValve(valve, 0, 128, 255))
    actions.append(Move(0.0))
    actions.append(Home(carefully=False))
    for ingredient in sorted_ingredients:
      valve = ingredients.IngredientNameToValvePosition(ingredient.name,
                                                        "Flush")
      actions.append(SetLedForValve(valve, 0, 0, 0))
    controller.EnqueueGroup(actions)


class HoldPressureHandler(webapp2.RequestHandler):
  def post(self):
    print "Hold pressure."
    controller.EnqueueGroup([HoldPressure()])


class ReleasePressureHandler(webapp2.RequestHandler):
  def post(self):
    controller.EnqueueGroup([ReleasePressure()])


class DispenseCupHandler(webapp2.RequestHandler):
  def post(self):
    controller.EnqueueGroup([DispenseCup()])


class DispenseCupFullTestHandler(webapp2.RequestHandler):
  def post(self):
    controller.EnqueueGroup([
        Move(CUP_DISPENSE_POSITION), DispenseCup(), Move(valve_position(0)),
        ReleaseCup()
    ])


class FillHandler(webapp2.RequestHandler):
  def post(self):
    print "FILL HANDLER"
    try:
      args = self.request.get('text').replace(" ", "").partition(",")
      valve = int(args[2])
      oz = float(args[0])
      controller.EnqueueGroup([
          SetLedForValve(valve, 255, 0, 0), Move(valve_position(valve)),
          SetLedForValve(valve, 0, 255, 0),
          Meter(valve_to_actuate=valve, oz_to_meter=oz),
          SetLedForValve(valve, 0, 128, 255)
      ])
    except ValueError:
      self.response.status = 400
      self.response.write("valve and oz arguments are required.")


class Test1Handler(webapp2.RequestHandler):
  def post(self):
    print "TEST1 HANDLER"
    try:
      test_drink = manual_db.TEST_DRINK
      controller.EnqueueGroup(actions_for_recipe(test_drink))
    except ValueError:
      self.response.status = 400
      self.response.write("valve and oz arguments are required.")


class CustomDrinkHandler(webapp2.RequestHandler):
  def post(self):
    try:
      recipe_obj = json.loads(self.request.get('recipe'))
      recipe = recipe_from_json_object(recipe_obj)
      print "Drink requested: %s", recipe
      controller.EnqueueGroup(actions_for_recipe(recipe))
      self.response.status = 200
      self.response.write("ok")
    except ValueError:
      print 'Error parsing custom drink request: %s' % (
          self.request.get('recipe', None))
      traceback.print_exc()
      self.response.status = 400
      self.response.write("valve and oz arguments are required.")


class MoveHandler(webapp2.RequestHandler):
  def post(self):
    print self.request
    controller.EnqueueGroup([Move(float(self.request.get('text')))])


class PausableWSGIApplication(webapp2.WSGIApplication):
  def __init__(self, routes=None, debug=False, config=None):
    super(PausableWSGIApplication, self).__init__(routes=routes,
                                                  debug=debug,
                                                  config=config)
    self.drop_all = False

  def __call__(self, environ, start_response):
    while self.drop_all:
      time.sleep(1.0)
    return super(PausableWSGIApplication, self).__call__(environ,
                                                         start_response)


def StartServer(port, syncer):
  from paste import httpserver
  logging.info("Starting server on port %d", port)
  #app = webapp2.WSGIApplication([
  app = PausableWSGIApplication([
      # User UI
      ('/all_drinks', AllDrinksHandler),
      ('/create_drink', CustomDrinkHandler),
      # User API
      ('/api/drink', DrinkHandler),
      # Debug UI
      ('/load_cell', ServeFile(STATIC_FILE_DIR + 'load_cell.html')),
      ('/load_cell.json', LoadCellJson),
      ('/queue', InspectQueue),
      ('/queue.json', InspectQueueJson),
      # Control API
      ('/queue-retry', RetryQueue),
      ('/queue-clear', ClearQueue),
      ('/queue-skip', SkipQueue),
      # Debug API
      ('/api/calibrate', SingleActionHandler(Home)),
      ('/api/compressor-on',
       SingleActionHandler(lambda: CompressorToggle(State.ON))),
      ('/api/compressor-off',
       SingleActionHandler(lambda: CompressorToggle(State.OFF))),
      ('/api/prime', PrimeHandler),
      ('/api/flush', FlushHandler),
      ('/api/hold_pressure', HoldPressureHandler),
      ('/api/release_pressure', ReleasePressureHandler),
      ('/api/dispense_cup', DispenseCupHandler),
      ('/api/dispense_cup_full_test', DispenseCupFullTestHandler),
      ('/api/move.*', MoveHandler),
      ('/api/fill.*', FillHandler),
      ('/api/test1.*', Test1Handler),
      # Default to serving static files.
      ('/', ServeFile(STATIC_FILE_DIR + 'index.html')),
      ('/.*', StaticFileHandler),
  ])
  controller.app = app
  controller.EnqueueGroup([HoldPressure()])
  if syncer: syncer.start()
  print "serving at http://%s:%i" % (socket.gethostname(), port)
  httpserver.serve(app, host="0.0.0.0", port=port, start_loop=True)


def main():
  FLAGS(sys.argv)

  # Set up logging
  rootLogger = logging.getLogger()
  rootLogger.setLevel(getattr(logging, FLAGS.loglevel.upper()))
  if FLAGS.logfile:
    rootLogger.addHandler(logging.FileHandler(FLAGS.logfile))
  if FLAGS.logtostderr:
    rootLogger.addHandler(logging.StreamHandler())

  global robot
  global controller
  if FLAGS.fake:
    robot = FakeRobot()
  else:
    from physical_robot import PhysicalRobot
    robot = PhysicalRobot()
  controller = Controller(robot)
  syncer = None
  if FLAGS.frontend:
    print 'Polling frontend at --frontend=%s' % FLAGS.frontend
    syncer = poll_appengine.SyncToServer(FLAGS.frontend + '/api/',
                                         FLAGS.fe_poll_freq, controller)
  StartServer(FLAGS.port, syncer)


if __name__ == "__main__":
  gflags.DEFINE_integer('port', 8000, 'Port to run on')
  gflags.DEFINE_bool('fake', False, 'Run with hardware faked out')
  gflags.DEFINE_string('logfile', '',
                       'File to log to. If empty, does not log to a file')
  gflags.DEFINE_boolean('logtostderr', True, 'Log to stderr instead of a file')
  gflags.DEFINE_enum('loglevel', 'info', ('debug', 'info', 'warning', 'error'),
                     'Log verbosity')
  gflags.DEFINE_string('frontend', '', 'Frontend server to sync with, if any')
  gflags.DEFINE_integer('fe_poll_freq', 5,
                        'Frontend polling frequency in seconds')
  main()
