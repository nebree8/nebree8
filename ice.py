#!/usr/bin/env python
import time

from physical_robot import PhysicalRobot
from actions.ice import DispenseIce, ICE_LOCATION
from actions.move import Move
from actions.led import SetLedForValve, Led
from parts import io_bank

robot = PhysicalRobot()


robot.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1, blocking=True)
robot.io.arduino.Servo(41, 90)
time.sleep(5)
robot.io.arduino.Servo(41, 0)
time.sleep(1.5)
robot.io.arduino.Servo(41, 90)
robot.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0, blocking=True)
time.sleep(1)
#   robot.BootStirMotor()
#   time.sleep(2)
#   led = Led(max(0, -10.65 - ICE_LOCATION), 255, 255, 0, y=4)
#   led(robot)
#   move = Move(ICE_LOCATION)
#   move(robot)
#   ice = DispenseIce()
#   ice(robot)
#   led = Led(max(0, -10.65 - ICE_LOCATION), 0, 128, 255, y=4)
#   led(robot)
#   time.sleep(3)
