from actions.action import Action, ActionException
import time

class DispenseCup(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    robot.LowerCup()
    time.sleep(1.0)
    robot.RaiseCup()
    time.sleep(1.0)
