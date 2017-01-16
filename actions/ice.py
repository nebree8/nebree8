from actions.action import Action, ActionException
#from actions.wait_for_glass_placed import WaitForGlassPlaced
import time


ICE_LOCATION = -58.375


class DispenseIce(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    robot.ChuckVent()
    robot.StartIce()
    time.sleep(2.9)
    #time.sleep(5.0)
    robot.StopIce()
    #WaitForGlassPlaced()(robot)
    time.sleep(2.2)
