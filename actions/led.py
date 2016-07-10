from actions.action import Action, ActionException


class Led(Action):
  def __init__(self, x, r, g, b, back=False, y=-1):
    self.x = x
    self.r = r
    self.g = g
    self.b = b
    if back:
      self.y = 8
    else:
      self.y = 0
    if y >= 0:
      self.y = y

  def __call__(self, robot):
    robot.SetLed(self.x, self.y, self.r, self.g, self.b)
    robot.UpdateLeds()


def led_position(valve_no):
  return 1.875 * valve_no


class SetLedForValve(Led):
  def __init__(self, valve, r, g, b):
    Led.__init__(self, max(0, led_position(valve) - 1.0), r, g, b,
                 valve % 2 == 1)
