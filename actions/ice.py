from actions.action import Action, ActionException
from parts import io_bank
import time
import threading


ICE_LOCATION = -54


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
    robot.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1, blocking=True)
    robot.io.arduino.Servo(41, 0)
    time.sleep(1.5)
    robot.io.arduino.Servo(41, 90)
