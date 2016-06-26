from actions.action import Action, ActionException
import time


class DispenseCup(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    robot.LowerCup()
    robot.ChuckVent()
    time.sleep(5.0)
    robot.RaiseCup()
    time.sleep(2.0)


class ReleaseCup(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    robot.Vent()
