#!/usr/bin/env python
import time
import common

r = common.make_robot()

for i in range(31):
  print "=== ", i
  with r.OpenValve(i):
    time.sleep(5)
