#!/usr/bin/env python
import time

import common

from parts.Adafruit_ADS1x15 import ADS1x15
from parts.Adafruit_I2C import Adafruit_I2C
Adafruit_I2C.getPiI2CBusNumber = staticmethod(lambda: 1)
ADS1115 = 1
adc = ADS1x15(ic=ADS1115)


def read():
  return adc.readADCSingleEnded(1, 4096, 128)


def fmt(v):
  if abs(v - initial) > 20:
    color = "31"
  elif abs(v - initial) > 10:
    color = "30"
  else:
    color = "37"
  return "\033[%sm% 4d\033[0m" % (color, (v % 1000))

initial = read()
readings = []
while True:
  if len(readings) == 11:
    readings.sort()
    avg = sum(readings) / len(readings)
    print ' [%s %sm %sa %s]' % (fmt(readings[0]), fmt(readings[5]), fmt(avg),
                                fmt(readings[-1]))
    readings = []
  v = read()
  readings.append(v)
  print fmt(v),
