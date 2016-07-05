"""Provides a layer of abstraction for setting output pins.

This lets the rest of the system assign a function to a pin, update that
function, etc. Handles details like some outputs being on shift registers,
etc."""

import enum
import threading
import time
import Queue
import RPi.GPIO as gpio
import arduino

DEBUG = True


def DebugPrint(*args):
  if DEBUG == True:
    print args
    #time.sleep(0.01)


class Outputs(enum.Enum):
  STEPPER_DIR = 7
  STEPPER_PULSE = 8
  STEPPER_ENABLE = 25

  # SHIFT_REG_CLOCK = 8
  # SHIFT_REG_RCLOCK = 25
  # SHIFT_REG_SERIAL = 7
  SHIFT_REG_CLOCK = 9
  SHIFT_REG_RCLOCK = 11
  SHIFT_REG_SERIAL = 10

  MOTOR_UP_A = 27
  MOTOR_UP_B = 22

  # VALVE_0 = 1019
  # VALVE_1 = 1001
  # VALVE_2 = 1002
  # VALVE_3 = 1003
  # VALVE_4 = 1004
  # VALVE_6 = 1005
  # VALVE_5 = 1006
  # VALVE_7 = 1007

  # VALVE_8 = 1014  # TO VERIFY
  # VALVE_9 = 1015  # TO VERIFY
  # VALVE_10 = 1011
  # VALVE_11 = 1010
  # VALVE_12 = 1009
  # VALVE_13 = 1008
  # VALVE_14 = 1012
  # VALVE_15 = 1013 # NOT CONNECTED

  # CHUCK = 1022
  # COMPRESSOR_HEAD = 1020
  # COMPRESSOR_VENT = 1021
  # # To pressurize, open head, close vent
  # # For chuck, close head, open vent
  # # For cleanup, open both
  # COMPRESSOR = 1023

  VALVE_0 = 2053
  VALVE_1 = 2011
  VALVE_2 = 2012  # orange
  VALVE_3 = 2010
  VALVE_4 = 2009

  VALVE_5 = 2005
  VALVE_6 = 2004
  VALVE_7 = 2003
  VALVE_8 = 2014
  VALVE_9 = 2002
  VALVE_10 = 2015
  VALVE_11 = 2016
  VALVE_12 = 2017

  VALVE_13 = 2018
  VALVE_14 = 2019
  VALVE_15 = 2022
  VALVE_16 = 2024
  VALVE_17 = 2026
  VALVE_18 = 2028
  VALVE_19 = 2030
  VALVE_20 = 2032

  VALVE_21 = 2039
  VALVE_22 = 2025
  VALVE_23 = 2027
  VALVE_24 = 2029
  VALVE_25 = 2031
  VALVE_26 = 2033
  VALVE_27 = 2035
  VALVE_28 = 2037

  VALVE_29 = 2046
  VALVE_30 = 2048

  CHUCK = 2008
  # COMPRESSOR_HEAD = 2004
  # COMPRESSOR_VENT = 2005
  # To pressurize, open head, close vent
  # For chuck, close head, open vent
  # For cleanup, open both
  COMPRESSOR = 2006
  ICE_DISPENSER = 2038


PRESSURE_VALVE_PIN = 7  # Not a normal output -- don't list with other valves. Should be controlled directly by the arduino.
#   ARDUINO_STEPPER_DONE = 44
#   ARDUINO_STEPPER_DIR = 42
#   ARDUINO_STEPPER_PULSE = 40
#   ARDUINO_STEPPER_ENABLE = 38
ARDUINO_STEPPER_DONE = 50
ARDUINO_STEPPER_DIR = 44
ARDUINO_STEPPER_PULSE = 42
ARDUINO_STEPPER_ENABLE = 40
ARDUINO_RAIL_TRIGGER_NEGATIVE = 36
ARDUINO_RAIL_TRIGGER_POSITIVE = 34

VALVES = (Outputs.VALVE_0,
          Outputs.VALVE_1,
          Outputs.VALVE_2,
          Outputs.VALVE_3,
          Outputs.VALVE_4,
          Outputs.VALVE_5,
          Outputs.VALVE_6,
          Outputs.VALVE_7,
          Outputs.VALVE_8,
          Outputs.VALVE_9,
          Outputs.VALVE_10,
          Outputs.VALVE_11,
          Outputs.VALVE_12,
          Outputs.VALVE_13,
          Outputs.VALVE_14,
          Outputs.VALVE_15,
          Outputs.VALVE_16,
          Outputs.VALVE_17,
          Outputs.VALVE_18,
          Outputs.VALVE_19,
          Outputs.VALVE_20,
          Outputs.VALVE_21,
          Outputs.VALVE_22,
          Outputs.VALVE_23,
          Outputs.VALVE_24,
          Outputs.VALVE_25,
          Outputs.VALVE_26,
          Outputs.VALVE_27,
          Outputs.VALVE_28,
          Outputs.VALVE_29,
          Outputs.VALVE_30,)


def GetValve(index):
  return VALVES[index]


class Inputs(enum.Enum):
  LIMIT_SWITCH_POS = 23
  LIMIT_SWITCH_NEG = 24


_SHIFT_REG_REFRESH_RATE = 10.
_SHIFT_REG_SLEEP_TIME = 0.0002  # 1 ms -> 1khz
_SHIFT_REG_ADDRESS_OFFSET = 1000
_ARDUINO_ADDRESS_OFFSET = 2000


class IOBank(object):
  def __init__(self, update_shift_reg=False, update_arduino=True):
    self.last_time = time.time()
    gpio.setmode(gpio.BCM)
    gpio.setwarnings(False)
    if update_arduino:
      self.arduino = arduino.Arduino()
    else:
      self.arduino = None
    for output in Outputs:
      if output.value < _SHIFT_REG_ADDRESS_OFFSET:
        gpio.setup(output.value, gpio.OUT)
      self.WriteOutput(output, 0)
    for pin in Inputs:
      gpio.setup(pin.value, gpio.IN, pull_up_down=gpio.PUD_UP)
    if update_shift_reg:
      self.current_shifted_byte = [0] * 24
      self.current_shifted_byte[Outputs.COMPRESSOR.value -
                                _SHIFT_REG_ADDRESS_OFFSET] = 1
      self.signal_refresh = Queue.Queue(1)
      self.thread = threading.Thread(target=self.__RefreshShiftOutputs)
      self.thread.daemon = True
      self.thread.start()
    self.WriteOutput(Outputs.COMPRESSOR, 0)

  def ReadInput(self, input_enum):
    return gpio.input(input_enum.value)

  # rising_or_falling should be gpio.RISING or gpio.FALLING
  def AddCallback(self, input_enum, rising_or_falling, callback):
    gpio.add_event_detect(input_enum.value,
                          rising_or_falling,
                          callback=callback)

  def WriteOutput(self, output_enum, value, blocking=False):
    if output_enum.value < _SHIFT_REG_ADDRESS_OFFSET:
      gpio.output(output_enum.value, value)
    elif output_enum.value < _ARDUINO_ADDRESS_OFFSET:
      # Shift register output.
      # Steps to write:
      # 1: update current shift reg bytes overall
      # 2: set bit, then toggle clock
      shift_register_index = output_enum.value - _SHIFT_REG_ADDRESS_OFFSET
      self.current_shifted_byte[shift_register_index] = value
      print "Update output: %s -> %s: %s" % (output_enum, value,
                                             self.current_shifted_byte)
      self.__SignalRefresh()
      time.sleep(0.1)
      if output_enum == Outputs.COMPRESSOR:
        time.sleep(0.5)
    else:
      if self.arduino:
        print "Arduino write (%d) = %d" % (
            output_enum.value - _ARDUINO_ADDRESS_OFFSET, value)
        self.arduino.WriteOutput(output_enum.value - _ARDUINO_ADDRESS_OFFSET,
                                 value, blocking=blocking)

  def HoldPressure(self):
    self.arduino.HoldPressure(PRESSURE_VALVE_PIN, hold=True)

  def ReleasePressure(self):
    self.arduino.HoldPressure(PRESSURE_VALVE_PIN, hold=False)

  def Move(self, forward, steps, final_wait, max_wait=4000):
    self.arduino.Move(ARDUINO_STEPPER_DIR, ARDUINO_STEPPER_PULSE,
                      ARDUINO_RAIL_TRIGGER_NEGATIVE,
                      ARDUINO_RAIL_TRIGGER_POSITIVE, ARDUINO_STEPPER_DONE,
                      forward, steps, final_wait, max_wait)
    #   start_time = time.time()
    #   while not self.ReadInput(Inputs.LIMIT_SWITCH_POS):
    #     time.sleep(0.05)
    #     if (time.time() - start_time > 4.0):
    #       break
    #   time.sleep(1.0)
    #   while self.ReadInput(Inputs.LIMIT_SWITCH_POS):
    #     time.sleep(0.05)

  def __Shift(self, byte):
    SLEEP_TIME = 0.0001
    byte = list(byte)
    if time.time() - self.last_time > 1.0:
      print "In __Shift() with bytes: %s" % byte
      self.last_time = time.time()
    byte.reverse()
    self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, gpio.LOW)
    for bitnum, bit in enumerate(byte):
      foodbit = bit
      self.WriteOutput(Outputs.SHIFT_REG_CLOCK, gpio.LOW)
      time.sleep(SLEEP_TIME)
      self.WriteOutput(Outputs.SHIFT_REG_SERIAL, foodbit)
      time.sleep(SLEEP_TIME)
      self.WriteOutput(Outputs.SHIFT_REG_CLOCK, gpio.HIGH)
      time.sleep(SLEEP_TIME)
    self.WriteOutput(Outputs.SHIFT_REG_CLOCK,
                     gpio.LOW)  # Reset to a safe state.
    #self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, gpio.LOW)
    #GPIO.output(gpiomap[swallow], GPIO.LOW)
    time.sleep(SLEEP_TIME)
    self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, gpio.HIGH)
    time.sleep(SLEEP_TIME)
    self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, gpio.LOW)
    #GPIO.output(gpiomap[swallow], GPIO.HIGH)

  def __RefreshShiftOutputs(self):
    old_compressor = 1
    new_compressor = 1
    while True:
      self.__Shift(self.current_shifted_byte)
      new_compressor = self.current_shifted_byte[Outputs.COMPRESSOR.value -
                                                 1000]
      if old_compressor != new_compressor:
        time.sleep(0.5)
      old_compressor = new_compressor
      try:
        self.signal_refresh.get(True, 1. / _SHIFT_REG_REFRESH_RATE)
      except Queue.Empty:
        pass  # No refresh signals for a while, refresh anyway.

  def __SignalRefresh(self):
    try:
      self.signal_refresh.put(None, False)
    except Queue.Full:
      pass  # Refresh already scheduled.
