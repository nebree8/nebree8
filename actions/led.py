from actions.action import Action, ActionException

class Led(Action):
  def __init__(self, x, r, g, b):
    self.x = x
    self.r = r
    self.g = g
    self.b = b

  def __call__(self, robot):
    robot.SetLed(self.x, 0, self.r, self.g, self.b)
