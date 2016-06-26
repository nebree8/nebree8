from actions.action import Action, ActionException


class HoldPressure(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    robot.HoldPressure()


class ReleasePressure(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    robot.ReleasePressure()
