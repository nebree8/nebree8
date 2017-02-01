#!/usr/bin/env python
import time

from physical_robot import PhysicalRobot
from actions.ice import PrepareIce, DispenseIce, ICE_LOCATION, StartIce, StopIce
from actions.move import Move
from actions.move_with_ice import MoveWithIce
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

move0 = Move(0)
move2 = Move(-2)
move57 = MoveWithIce(-57, 0.5)
move0(robot)
for i in range(50):
    move2(robot)
    move57(robot)
    time.sleep(1)
time.sleep(10)
print "booting down."
