from actions.action import Action, ActionException
import time


class DispenseIce(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    robot.ChuckVent()
    robot.StartIce()
    time.sleep(1.7)
    robot.StopIce()
    time.sleep(3.0)
