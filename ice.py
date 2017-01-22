#!/usr/bin/env python
import time

from physical_robot import PhysicalRobot
from actions.ice import PrepareIce, DispenseIce, ICE_LOCATION, StartIce, StopIce
from actions.move import Move
from actions.led import SetLedForValve, Led
from parts import io_bank

robot = PhysicalRobot()

time.sleep(2)
#robot.io.nano.WriteDelayRaw(13, 1, 2)
#   robot.io.nano.Blink(13, 0.2)
#   time.sleep(2)
#   robot.io.nano.Blink(13, 3)
#   ice_door = DispenseIce()
#   ice_door(robot)
#   time.sleep(2)
#   robot.io.nano.Blink(13, 0.2)
#   time.sleep(2)
#robot.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1, blocking=True)
robot.io.arduino.Servo(41, 90)

move = Move(0)
move(robot)
#robot.io.arduino.WriteDelayRaw(12, 1, 3)
time.sleep(0.2)
#prep_ice = PrepareIce()
#prep_ice(robot)
#   prep_ice = StartIce()
#   prep_ice(robot)
#   prep_ice = StopIce()
#   prep_ice(robot)
#time.sleep(6)
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
