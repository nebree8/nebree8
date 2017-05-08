import time
import logging

from actions.action import Action, ActionException
from actions import meter_common


ICE_LOCATION = -56.5


class StartIce(Action):
  def __init__(self):
    pass
  def __call__(self, robot):
    robot.StartIce()

class StopIce(Action):
  def __init__(self):
    pass
  def __call__(self, robot):
    robot.StopIce()

class PrepareIce(Action):
  def __init__(self):
    pass
  def __call__(self, robot):
    robot.PrepIce()

class DispenseIce(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    with robot.DispenseIce():
      time.sleep(1.5)

class DispenseIceWithRetry(Action):
  def __init__(self, min_oz_to_meter=1.0):
    self.min_oz_to_meter = min_oz_to_meter
    self.tare = None
    self.target_reading = None
    self.current_reading = None
    self.final_reading = None

  def __call__(self, robot):
    self.tare = robot.load_cell.recent_summary(n=2)
    self.target_reading = (
        self.tare.mean + meter_common.OZ_TO_ADC_VALUES * self.min_oz_to_meter)
    first = True
    for i in range(3):  #  Try at most three times
      if not first:
          robot.StartIce()
          time.sleep(3.0)
          robot.StopIce()
      first = False
      with robot.DispenseIce():
        time.sleep(1.5)
      time.sleep(.5)
      self.current_reading = robot.load_cell.recent_summary(n=2)
      if self.current_reading.mean > self.target_reading:
        break
      logging.info("retrying ice; target_reading=%s, current_reading=%s",
                   self.target_reading, self.current_reading.mean)
      # retry
    self.final_reading = self.current_reading
