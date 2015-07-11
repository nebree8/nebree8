import struct
import threading
import time
import Queue

from arduinoio import serial_control

_REFRESH_RATE = 5  # Refreshes per second

class Arduino:
  def __init__(self):
    self.interface = serial_control.SerialInterface()
    self.outputs = {}
    self.signal_refresh = Queue.Queue(1)
    self.incoming_messages = Queue.Queue(10)
    self.thread = threading.Thread(target=self.__RefreshOutputs)
    self.thread.daemon = True
    self.thread.start()

  def WriteOutput(self, pin, value):
    self.outputs[pin] = value
    try:
      self.signal_refresh.put((False, None), block=False, timeout=None)
    except Queue.Full:
      pass

  def WriteServo(self, pin, start_degrees, end_degrees, seconds):
    raw_message = [chr(pin), chr(start_degrees), chr(end_degrees), chr(seconds)]
    command = "SERVO" + "".join(raw_message)
    self.interface.Write(0, command)
    print "set servo"

  def HoldPressure(self, pressure_valve_pin, hold=True):
    min_pressure_psi = 15.5
    max_pressure_psi = 15.8
    min_pressure_mbar = min_pressure_psi * 1014 / 14.7
    max_pressure_mbar = max_pressure_psi * 1014 / 14.7
    raw_message = []
    raw_message.extend(struct.unpack('4B', struct.pack('<f', min_pressure_mbar)))
    raw_message.extend(struct.unpack('4B', struct.pack('<f', max_pressure_mbar)))
    raw_message = [chr(x) for x in raw_message]
    raw_message.extend((chr(hold), chr(pressure_valve_pin)))
    command = "HOLDP" + "".join(raw_message)
    self.signal_refresh.put((True, command), block=True, timeout=None)

  def Move(self, stepper_dir_pin, stepper_pulse_pin, negative_trigger_pin,
      positive_trigger_pin, done_pin, forward, steps, final_wait):
    raw_message = []
    if forward:
      forward = 0x01
    else:
      forward = 0x00
    raw_message.extend((
      stepper_dir_pin, stepper_pulse_pin, negative_trigger_pin, positive_trigger_pin, done_pin, forward))
    raw_message.extend(struct.unpack('4B', struct.pack('<i', steps)))
    raw_message.extend(struct.unpack('4B', struct.pack('<i', int(1.0 / final_wait))))
    raw_message = [chr(x) for x in raw_message]
    command = "MOVE" + "".join(raw_message)
    print "Move command: %s" % [ord(x) for x in raw_message]
    self.signal_refresh.put((True, command), block=True, timeout=None)


  def __SendOutputsMessage(self):
    raw_message = []
    for pin, value in self.outputs.iteritems():
      raw_message.append(chr(pin))
      raw_message.append(chr(value))
    command = "SET_IO" + "".join(raw_message)
    self.interface.Write(0, command)

  def __RefreshOutputs(self):
    while True:
      try:
        use_this_command, command = self.signal_refresh.get(True, 1. / _REFRESH_RATE)
        if use_this_command:
          self.interface.Write(0, command)
          #f command[0:4] == "MOVE":
          # print "Wait for motor."
          # while True:
          #   message = self.interface.Read(no_checksums=True)
          #   if message:
          #     print "Got message: %s" % message.command
          #     if message.command[0:5] == [ord(x) for x in "MDONE"]:
          #       print "Motor done."
          #       break
        else:
          self.__SendOutputsMessage()
      except Queue.Empty:
        # No refresh signals for a while, Refresh all pins
        self.__SendOutputsMessage()
      message = None#self.interface.Read(no_checksums=True)
      if message:
        try:
          self.incoming_messages.put((False, None), block=False, timeout=None)
        except Queue.Full:
          pass


def main():
  arduino = Arduino()
  while True:
    arduino.WriteOutput(2, 1)
    time.sleep(1.0)
    for pin in [6, 13, 12, 11, 10, 9, 2]:
      for setting in [0, 1]:
        arduino.WriteOutput(pin, setting)
        time.sleep(1.0)
    time.sleep(5)
    print "should be done"

  # end = 160
  # middle = 100
  # ts = 3
  # arduino.WriteServo(22, end, middle, ts)
  # arduino.WriteServo(21, 180, 90, ts)
  # time.sleep(10)
  # print "should be done"
  # time.sleep(2)
  # arduino.WriteServo(22, 90, 180, ts)
  # arduino.WriteServo(21, 90, 180, ts)
  # time.sleep(10)
  # print "should be done"


if __name__ == "__main__":
  main()
