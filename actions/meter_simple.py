#!/usr/bin/env python
import logging
import time

from actions.action import Action
from actions import meter_common

METER_OZ_OFFSET = 0.0


class MeterSimple(Action):
  def __init__(self, valve_to_actuate, oz_to_meter):
    self.valve_to_actuate = valve_to_actuate
    self.oz_to_meter = oz_to_meter

  def __call__(self, robot):
    robot.Vent()
    if self.oz_to_meter == 0:
      logging.warning("oz_to_meter was zero, returning early.")
    self.initial_reading = robot.load_cell.recent_summary(secs=.2).mean
    tare = meter_common.tare(robot)
    self.tare_reading = tare.mean
    if not tare.healthy:
      self.unhealthy = True
      logging.error("UNHEALTHY TARE")
      with robot.OpenValve(self.valve_to_actuate):
        time.sleep(meter_common.SECONDS_PER_OZ * self.oz_to_meter)
        return
    self.target_reading = (tare.mean + meter_common.OZ_TO_ADC_VALUES * max(
        self.oz_to_meter - METER_OZ_OFFSET, .1))
    last_summary = tare
    print "Metering to oz %f or %s" % (self.oz_to_meter, self.target_reading)
    with robot.OpenValve(self.valve_to_actuate):
      while last_summary.mean < self.target_reading:
        time.sleep(.05)
        last_summary = robot.load_cell.recent_summary(secs=.1)
        self.current_reading = last_summary.mean
      self.final_reading = self.current_reading
    #time.sleep(1)
    #   r = robot.load_cell.recent(secs=time.time() - tare.timestamp + 5)
    #   f = open('readings/readings_%s_%foz.csv' %
    #            (time.strftime("%Y%m%d_%H%M%S"), self.oz_to_meter), 'w')
    #   for ts, v in r:
    #     print >> f, "%s,%s" % (ts, v)
    #   f.close()
