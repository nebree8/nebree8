#!/usr/bin/env python
import time
import common
from actions.led import SetLedForValve

r = common.make_robot()

print """
Opening each valve, starting from the left/home side. Hit enter to move to the
next valve.
"""

r.ActivateCompressor()
for i in range(31):
  print "=== ", i
  SetLedForValve(i, 255, 255, 255)(r)
  with r.OpenValve(i):
    raw_input()
