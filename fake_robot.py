import time

import gflags

from actions.action import ActionException
from contextlib import contextmanager
from parts.load_cell import FakeLoadCellMonitor
from robot import Robot

FLAGS = gflags.FLAGS
gflags.DEFINE_boolean("fake_sleep", True, "sleep() in the fake")

def _sleep(secs):
  if FLAGS.fake_sleep:
    time.sleep(secs)


class FakeRobot(Robot):
  def __init__(self):
    import collections
    self.position = 30.0
    self.load_cell = FakeLoadCellMonitor()
    self.load_cell.stddev = 1
    self.valves = collections.defaultdict(lambda: False)
    self.pressurized = False

  def __check_position(self, valve_no):
    if abs(self.position - (-9.625 - 1.875 * valve_no)) > 1:
      raise ActionException("Caddy wasn't in the right position!")

  @staticmethod
  def __run_with_delay(delay_sec, fn):
    import threading

    def W():
      _sleep(delay_sec)
      fn()

    t = threading.Thread(target=W)
    t.daemon = True
    t.start()

  def __set_load_cell_attrs(self, load_per_second=0, stddev=1):
    self.load_cell.load_per_second = load_per_second
    self.load_cell.stddev = stddev

  def CalibrateToZero(self, carefully=False):
    self._FakeMove(0)

  def MoveToPosition(self, position_in_inches):
    old_stddev = self.load_cell.stddev
    self.load_cell.stddev *= 10
    self._FakeMove(position_in_inches)
    self.load_cell.stddev = old_stddev

  @contextmanager
  def OpenValve(self, valve_no):
    if self.valves[valve_no]:
      raise ActionException("Valve %s was already open!" % valve_no)
    self.valves[valve_no] = True
    self.__check_position(valve_no)
    self.__run_with_delay(
        .25,
        lambda: self.__set_load_cell_attrs(load_per_second=10, stddev=10))
    yield
    if not self.valves[valve_no]:
      raise ActionException("Valve %s wasn't open!" % valve_no)
    self.__check_position(valve_no)
    self.valves[valve_no] = False
    self.__run_with_delay(
        .25,
        lambda: self.__set_load_cell_attrs(load_per_second=0, stddev=1))

  def ActivateCompressor(self):
    return

  def DeactivateCompressor(self):
    return

  def HoldPressure(self):
    """Maintains a min/max pressure range in the vessel."""
    self.pressurized = True

  def ReleasePressure(self):
    """Stops maintaining pressure -- may leak out quickly or slowly."""
    self.pressurized = False

  def SetLed(self, x, y, r, g, b):
    pass

  def UpdateLeds(self):
    pass

  def AllLed(self, r, g, b):
    pass

  def StartIce(self):
    _sleep(2.0)

  def StopIce(self):
    pass

  def BootStirMotor(self):
    time.sleep(0.1)
    self.StopStirMotor()

  def CleanStirMotor(self):
    time.sleep(1)
    self.StopStirMotor()

  def StartStirMotor(self):
    pass

  def StopStirMotor(self):
    pass

  def GentleStir(self):
    on_sleep_secs = 0.4
    off_sleep_secs = 0.3
    for i in range(6):
      _sleep(on_sleep_secs)
      _sleep(off_sleep_secs)
  
  def _FakeMove(self, new_position):
    _sleep(abs(self.position - new_position) / 10.0)
    self.position = new_position * 1.0

  def ChuckVent(self):
    pass

  def GentleStir(self):
    pass

  def CleanStirMotor(self):
    pass

  @contextmanager
  def DispenseIce(self):
    yield

  def PrepIce(self):
    return
