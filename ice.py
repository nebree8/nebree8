#!/usr/bin/env python
import time

from physical_robot import PhysicalRobot
from actions.ice import PrepareIce, DispenseIce, ICE_LOCATION, StartIce, StopIce
from actions.move import Move
from actions.led import SetLedForValve, Led
from parts import io_bank

robot = PhysicalRobot()

robot.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1, blocking=True)
robot.io.arduino.Servo(41, 90)

move = Move(0)
move(robot)
prep_ice = StartIce()
prep_ice(robot)
move = Move(ICE_LOCATION / 2)
move(robot)
prep_ice = StopIce()
prep_ice(robot)
move = Move(ICE_LOCATION)
move(robot)
led = Led(max(0, -11.15 - ICE_LOCATION), 0, 128, 255, y=4)
led(robot)

ice_door = DispenseIce()
ice_door(robot)

robot.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0, blocking=True)
time.sleep(2)
#   robot.BootStirMotor()
#   time.sleep(2)
#   led = Led(max(0, -10.65 - ICE_LOCATION), 255, 255, 0, y=4)
#   led(robot)
