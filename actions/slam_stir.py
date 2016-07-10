from actions.action import Action, ActionException
import time


class SlamStir(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    robot.ChuckVent()
    time.sleep(1.0)
    robot.Slam()
    robot.GentleStir()
    robot.StopStirMotor()
    robot.UnSlam()
    time.sleep(1.0)
    robot.CleanStirMotor()
    time.sleep(1.0)
