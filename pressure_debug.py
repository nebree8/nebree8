import struct
import time
import threading
import Queue

from arduinoio import serial_control
import arduino

def ReadMessageAndReturn(interface):
  start = time.time()
  while True:
    message = interface.Read(no_checksums=True)
    if message:
      print "Len = %d" % len(message.command)
      if len(message.command) == 8:
        print "Set IO: %d %d" % (message.command[6],
                                 message.command[7])
        if time.time() - start > 3.0:
          return
      else:
        print "Pressure:"
        pressures = []
        for i in range(3):
          float_bytes = message.command[i * 4:(i + 1) * 4]
          mbar = struct.unpack('<f', struct.pack('4B', *float_bytes))[0]
          pressures.append(str(mbar / 1013.52932 * 14.7))
        print "Pressures: (psi) %s" % " ".join(pressures)
        print "state = %d" % message.command[12]
        return

def old_test():
  interface = serial_control.SerialInterface()
  while True:
    interface.Write(0, "GETP")
    ReadMessageAndReturn(ard.interface)
    time.sleep(1.0)


def new_test():
  ard = arduino.Arduino()
  ard.HoldPressure(7, hold=False)
  #ard.HoldPressure(7, hold=True)
  while True:
    for hold in [True]:#, False):
      print "Hold Pressure."
      #ard.HoldPressure(7, hold=hold)
      #ReadMessageAndReturn(ard.interface)
      time.sleep(0.1)
      ard.interface.Write(0, "GETP")
      time.sleep(0.2)
      ReadMessageAndReturn(ard.interface)
      # while True:
      #   try:
      #     print ard.incoming_messages.get(block=False)
      #   except Queue.Empty:
      #     break
      #time.sleep(2.0)


def main():
  new_test()

if __name__ == "__main__":
  main()
