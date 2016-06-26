from actions.action import Action, ActionException
import time


class DispenseIce(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    robot.ChuckVent()
    robot.LowerCup()
    time.sleep(3.0)
    robot.RaiseCup()
    time.sleep(3.0)
