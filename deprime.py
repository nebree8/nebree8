#!/usr/bin/env python
import time
from physical_robot import PhysicalRobot

r = PhysicalRobot()

for i in range(31):
  print "=== ", i
  with r.OpenValve(i):
    time.sleep(5)
