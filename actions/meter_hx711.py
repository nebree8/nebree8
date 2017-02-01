#!/usr/bin/env python

from actions.action import Action
from actions import meter_common

METER_OZ_OFFSET = 0.0


class MeterHX711(Action):
  def __init__(self, valve_to_actuate, oz_to_meter):
    self.valve_to_actuate = valve_to_actuate
    self.oz_to_meter = oz_to_meter

  def __call__(self, robot
    self.initial_reading = robot.io_bank.load_cell_reading
    self.target_reading = (self.initial_reading + meter_common.OZ_TO_ADC_VALUES * max(
        self.oz_to_meter - METER_OZ_OFFSET, .1))
    with robot.OpenValve(self.valve_to_actuate):
      while robot.io_bank.load_cell_reading < self.target_reading:
        time.sleep(.05)
