"""Waits for the glas to be placed on the caddy"""

from time import sleep

from actions.action import Action


class WaitForGlassPlaced(Action):
  def __call__(self, robot):
    self.force = False
    sleep(.1)
    self.initial = robot.load_cell.recent_summary(n=2)
    if not self.initial.healthy:
      print "unhealthy load cell; sleeping 15s"
      sleep(15)
      return
    sleep(.1)
    target = self.initial.mean + 0.2
    print "waiting for: %f" % target
    while True:
      self.summary = robot.load_cell.recent_summary(n=2)
      if (self.summary.mean > target or self.force):
        return
