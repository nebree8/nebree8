"""Waits for glass to be removed, based on weight"""

from time import sleep

from actions.action import Action

class WaitForGlassRemoval(Action):
    def __init__(self, user_name, recipe):
      self.user_name = user_name
      self.recipe = recipe

    def __call__(self, robot):
      sleep(.1)
      self.initial = robot.load_cell.recent_summary(secs=.1)
      if not self.initial.healthy:
        return
      sleep(.1)
      while True:
        self.summary = robot.load_cell.recent_summary(secs=.1)
        if self.summary.mean < self.initial.mean - self.initial.stddev * 3:
          return
