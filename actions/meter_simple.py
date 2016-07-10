#!/usr/bin/env python
import logging
import time

from actions.action import Action

METER_OZ_OFFSET = 0.4
OZ_TO_ADC_VALUES = 35
TIME_PER_OZ = 13.5
TARE_TIMEOUT_SECS = 20.
MAX_TARE_STDDEV = 3.


# class MeterSimple(Action):
#   def __init__(self, valve_to_actuate, oz_to_meter):
#     self.valve_to_actuate = valve_to_actuate
#     self.oz_to_meter = oz_to_meter
#   def __call__(self, robot):
#     if self.oz_to_meter == 0:
#       logging.warning("oz_to_meter was zero, returning early.")
#     with robot.OpenValve(self.valve_to_actuate):
#       time.sleep(13.5 * self.oz_to_meter)
#     time.sleep(1)
class MeterSimple(Action):
  def __init__(self, valve_to_actuate, oz_to_meter):
    self.valve_to_actuate = valve_to_actuate
    self.oz_to_meter = oz_to_meter

  def __call__(self, robot):
    if self.oz_to_meter == 0:
      logging.warning("oz_to_meter was zero, returning early.")
    self.initial_reading = robot.load_cell.recent_summary(secs=.2).mean
    tare = self._tare(robot)
    self.tare_reading = tare.mean
    if not tare.healthy:
      logging.info("UNHEALTHY TARE")
      with robot.OpenValve(self.valve_to_actuate):
        time.sleep(TIME_PER_OZ * self.oz_to_meter)
        return
    self.target_reading = (tare.mean + OZ_TO_ADC_VALUES * max(
        self.oz_to_meter - METER_OZ_OFFSET, .05))
    last_summary = tare
    print "Metering to oz %f or %s" % (self.oz_to_meter, self.target_reading)
    with robot.OpenValve(self.valve_to_actuate):
      logging.info("healthy tare")
      while last_summary.mean < self.target_reading:
        time.sleep(.05)
        last_summary = robot.load_cell.recent_summary(secs=.1)
        self.current_reading = last_summary.mean
      self.final_reading = self.current_reading
    time.sleep(1)
    r = robot.load_cell.recent(secs=time.time() - tare.timestamp + 5)
    f = open('readings/readings_%s_%foz.csv' %
             (time.strftime("%Y%m%d_%H%M%S"), self.oz_to_meter), 'w')
    for ts, v in r:
      print >> f, "%s,%s" % (ts, v)
    f.close()

  def _tare(self, robot):
    """Waits for load cell readings to stabilize.

    returns: load_cell.Summary
    throws: Exception
    """
    tare_start = time.time()
    tare = robot.load_cell.recent_summary(secs=.1)
    while (tare.stddev > MAX_TARE_STDDEV and
           time.time() < tare_start + TARE_TIMEOUT_SECS):
      time.sleep(.1)
      tare = robot.load_cell.recent_summary(secs=.1)
    if tare.stddev > MAX_TARE_STDDEV:
      logging.error('Reading standard deviation while taring above ' +
                    '%s for %s secs. Last result: %s' %
                    (MAX_TARE_STDDEV, TARE_TIMEOUT_SECS, tare))
    return tare
