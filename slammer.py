#!/usr/bin/env python
import time

from physical_robot import PhysicalRobot
from actions.slam_stir import SlamStir

robot = PhysicalRobot()
robot.BootStirMotor()
time.sleep(2)
slam_stir = SlamStir()
slam_stir(robot)
