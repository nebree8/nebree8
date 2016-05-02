import physical_robot
import time


def clamp(color):
  color = color % 256
  return color


class LedShow(object):
  def __init__(self, robot):
    self.r = 0
    self.g = 200
    self.b = 200
    self.robot = robot

    self.index = 0
    self.rindex = 179

  def Update(self):
    print "Led show!"
    self.r = clamp(self.r + 4)
    self.g = clamp(self.g * 2 + 1)
    self.b = clamp(self.b + 12)

    self.index += 1
    self.index = self.index % 180
    self.rindex -= 1
    if self.rindex < 0:
      self.rindex = 179

    self.robot.AllLed(0, 0, 0)
    self.SetFromIndex(self.index)
    self.SetFromIndex(self.rindex)
    self.robot.UpdateLeds()
    print "Led show done!"

  def SetFromIndex(self, index):
    x = (index % 60)
    y = int(index / 60) * 4
    if y == 4:
      x = 60 - x
    self.robot.SetLed(x, y, self.r, self.g, self.b)

  def Clear(self):
    self.robot.AllLed(0, 0, 0)
    self.robot.UpdateLeds()
