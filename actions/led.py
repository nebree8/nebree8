from actions.action import Action, ActionException

class Led(Action):
  def __init__(self, x, r, g, b, back=False):
    self.x = x
    self.r = r
    self.g = g
    self.b = b
    if back:
      self.y = 8
    else:
      self.y = 0

  def __call__(self, robot):
    robot.SetLed(self.x, self.y, self.r, self.g, self.b)
    robot.UpdateLeds()
