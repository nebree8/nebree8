#!/usr/bin/env python
import time

from physical_robot import PhysicalRobot

robot = PhysicalRobot()
actions = (
        ("*** START ***", robot.BootStirMotor, 1),
        ("===STOP===", robot.StopStirMotor, 1),
        ("*** START ***", robot.GentleStir, 2),
        ("===STOP===", robot.StopStirMotor, 5),
        ("===STOP===", robot.CleanStirMotor, 0),
        )
for name, action, sleep in actions:
  print name
  action()
  time.sleep(sleep)
