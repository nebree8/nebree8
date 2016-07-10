from actions.action import Action, ActionException
import time


class SlamStir(Action):
  def __init__(self):
    pass

  def __call__(self, robot):
    robot.ChuckVent()
    robot.Slam()
    robot.GentleStir()
    robot.StopStirMotor()
    robot.UnSlam()
    robot.CleanStirMotor()
    time.sleep(4.0)
