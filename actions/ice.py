from actions.action import Action, ActionException
import time


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
