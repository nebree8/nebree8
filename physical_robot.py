from contextlib import contextmanager
import logging
import time

from parts import io_bank
from robot import Robot
from parts.load_cell import LoadCellMonitor
from parts.motor import StepperMotor, RobotRail


def IngredientToValve(ingredient_index):
  return Outputs(1000 + ingredient_index)


class PhysicalRobot(Robot):
  """Implementation of Robot that interfaces with real hardware."""

  def __init__(self):
    self.io = io_bank.IOBank()
    motor = StepperMotor(io=self.io, use_separate_process=True)  # Not a dry run
    self.rail = RobotRail(motor)
    self.load_cell = LoadCellMonitor()
    self.calibrated = False
    self.pressurized = False
    self.BootStirMotor()

  def CalibrateToZero(self, carefully=True):
    self.ActivateCompressor()
    time.sleep(0.5)
    self.cannot_interrupt = True
    self.rail.CalibrateToZero()
    self.cannot_interrupt = False
    self.DeactivateCompressor()
    self.calibrated = True

  def MoveToPosition(self, position_in_inches):
    if not self.calibrated:
      self.CalibrateToZero()
    self.cannot_interrupt = True
    self.ChuckHoldHeadPressure()
    time.sleep(0.5)
    logging.info("Moving")
    self.rail.FillPositions([position_in_inches])
    logging.info("Move Done")
    #self.Vent()
    self.cannot_interrupt = False
    if position_in_inches < -65.25:
      self.rail.position = -65.25

  def PressurizeHead(self):
    print "Pressurize Head"
    #self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_HEAD, 1)
    #self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 0)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1)
    self.io.WriteOutput(io_bank.Outputs.CHUCK, 0)

  def Vent(self):
    #self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_HEAD, 1)
    #self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 1)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0, blocking=True)

  def ChuckVent(self):
    """Runs the compressor and holds the chuck."""
    # self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_HEAD, 1)
    # self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 1)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1, blocking=True)
    #self.io.WriteOutput(io_bank.Outputs.CHUCK, 0)

  def StartIce(self):
    """Starts the ice dispenser."""
    self.io.WriteOutput(io_bank.Outputs.ICE_DISPENSER, 1, blocking=True)

  def ToggleIceDoor(self):
    self.io.arduino.Servo(41, 0)
    time.sleep(2)
    self.io.arduino.Servo(41, 90)

  def StopIce(self):
    """Stops the ice dispenser."""
    self.io.WriteOutput(io_bank.Outputs.ICE_DISPENSER, 0, blocking=True)

  def ChuckHoldHeadPressure(self):
    return self.ChuckVent()
    # self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_HEAD, 0)
    # self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 1)
    # self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0)
    # self.io.WriteOutput(io_bank.Outputs.CHUCK, 0)

  def CompressorLock(self):
    # self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_HEAD, 0)
    # self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 1)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0, blocking=True)
    #time.sleep(0.5)
    # self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 0)
    self.io.WriteOutput(io_bank.Outputs.CHUCK, 0, blocking=True)

  def HoldPressure(self):
    """Maintains a min/max pressure range in the vessel."""
    print "physical_robot hold pressure."
    self.io.HoldPressure()
    self.pressurized = True

  def ReleasePressure(self):
    """Stops maintaining pressure -- may leak out quickly or slowly."""
    self.io.ReleasePressure()
    self.pressurized = False

  @contextmanager
  def OpenValve(self, valve_no):
    valve_io = io_bank.GetValve(valve_no)
    self.io.WriteOutput(valve_io, 1, blocking=True)
    logging.info("OPEN VALVE: %d -> %s (wired at %d)",
                 valve_no, valve_io, valve_io.value)
    yield
    self.io.WriteOutput(valve_io, 0, blocking=True)
    logging.info("CLOSE VALVE: %s", valve_io)

  def ActivateCompressor(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1, blocking=True)

  def DeactivateCompressor(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0, blocking=True)

  def SetLed(self, x, y, r, g, b):
    self.io.arduino.SetLed(x, y, r, g, b)

  def AllLed(self, r, g, b):
    self.io.arduino.AllLed(r, g, b)

  def UpdateLeds(self):
    self.io.arduino.UpdateLeds()

  def Shake(self):
    self.ChuckHoldHeadPressure()
    time.sleep(2.0)
    for i in range(8):
      steps = 100
      min_wait = 250  # us
      self.io.Move(True, steps, min_wait, max_wait=400)
      self.io.Move(False, steps, min_wait, max_wait=400)

  def BootStirMotor(self):
    self.io.arduino.Servo(13, 90)
    time.sleep(0.1)
    self.StopStirMotor()

  def CleanStirMotor(self):
    self.io.arduino.Servo(13, 90)
    time.sleep(3)
    self.StopStirMotor()

  def GentleStir(self):
    on_sleep_secs = 0.2
    #on_sleep_secs = 0.18
    off_sleep_secs = 0.13
    for i in range(8):
      self.io.arduino.Servo(13, 50)
      time.sleep(on_sleep_secs)
      self.StopStirMotor()
      time.sleep(off_sleep_secs)

  def StopStirMotor(self):
    self.io.arduino.Servo(13, 30)

  def Slam(self):
    self.io.WriteOutput(io_bank.Outputs.SLAM, 1, blocking=True)

  def UnSlam(self):
    self.io.WriteOutput(io_bank.Outputs.SLAM, 0, blocking=True)

  @contextmanager
  def DispenseIce(self):
    robot.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1, blocking=True)
    robot.io.arduino.Servo(41, 0)
    yield
    robot.io.arduino.Servo(41, 90)

  def PrepIce(self):
    secs = 3.0
    self.io.arduino.WriteDelay(io_bank.Outputs.ICE_DISPENSER, 1, secs)
