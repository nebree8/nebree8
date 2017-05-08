#!/usr/bin/env python
import time

import arduino
from parts import motor


uno = arduino.Arduino("ttyACM1", baud=9600)
time.sleep(2)
print ("change blink")
uno.Blink(13, 0.3)
print ("sleep")
print ("motor")
DIR_PIN = 12
STEP_PIN = 11
# UNCONNECTED
TRIGGER_NEG = 10
TRIGGER_POS = 9
STEPPER_DONE = 8
ICE_PIN = 7
ICE_STEPS = 6

forward = 1
steps = 19928
final_wait = 1000
max_wait = 4000
for i in range(10):
    uno.Move(DIR_PIN, STEP_PIN, TRIGGER_NEG, TRIGGER_POS, STEPPER_DONE, forward, steps, final_wait, max_wait, ICE_PIN, ICE_STEPS)
    time.sleep(10)
