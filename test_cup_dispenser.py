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
# Protoboard
#DIR_PIN = 12
#STEP_PIN = 11
DIR_PIN = 3
STEP_PIN = 2
# UNCONNECTED
TRIGGER_NEG = 10
TRIGGER_POS = 9
STEPPER_DONE = 8
ICE_PIN = 7
ICE_STEPS = 6

forward = 1
steps = 200
final_wait = 4000
max_wait = 4000
print steps
for i in range(50):
    uno.Move(DIR_PIN, STEP_PIN, TRIGGER_NEG, TRIGGER_POS, STEPPER_DONE, forward, steps, final_wait, max_wait, ICE_PIN, ICE_STEPS)
    time.sleep(2)

# NOTE, may need to ground the enable pin beyond default wiring.
