"""Move the caddy to an absolute position"""

import time

from actions.action import Action


class MoveWithIce(Action):
  def __init__(self, position_in_inches, ice_percent):
    self.position_in_inches = position_in_inches
    self.ice_percent = ice_percent

  def __call__(self, robot):
    robot.MoveToPosition(self.position_in_inches, ice_percent=self.ice_percent)

  def sensitive(self):
    return True
