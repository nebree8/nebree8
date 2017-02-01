#!/usr/bin/python

import math
import random
import time
import threading
import serial

from collections import deque, namedtuple

SAMPLES_PER_SECOND = 128
ADS1115 = 1

Summary = namedtuple('Summary',
                     ['records', 'mean', 'stddev', 'timestamp', 'healthy'])


class LoadCellMonitor(threading.Thread):
  """Continuously monitors and logs weight sensor readings."""

  def __init__(self, bufsize=10000, adc=None):
    super(LoadCellMonitor, self).__init__()
    self.nano_ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=0, rtscts=True)  # 1s timeout
    time.sleep(1)
    self.lock = threading.Lock()
    self.buffer = deque(maxlen=bufsize)
    self.shutdown = False
    self.daemon = True
    self.start()

  def recent_secs(self, secs):
    r = []
    threshold = time.time() - secs
    with self.lock:
      for i in reversed(self.buffer):
        if i[0] < threshold: break
        r.append(i)
    return r

  def recent_n(self, n):
    r = []
    with self.lock:
      for i in reversed(self.buffer):
        if len(r) >= n: break
        r.append(i)
    return r

  def recent(self, n=0, secs=0):
    """Return the last n readings as (time, value) tuples."""
    if secs > 0:
      return self.recent_secs(secs)
    elif n > 0:
      return self.recent_n(n)
    else:
      return []

  def recent_summary(self, n=0, secs=0):
    """Return a Summary of the last n readings."""
    recs = self.recent(n, secs)
    n = len(recs)
    if n == 0:
      return Summary([], 0, 0, time.time(), True)
    mean = sum(v for t, v in recs) / n
    if n > 1:
      stddev = math.sqrt(sum((v - mean)**2 for t, v in recs) / (n - 1))
    else:
      stddev = 0.
    healthy = mean != 0.0
    return Summary(recs, mean, stddev, max(ts for ts, v in recs), healthy)

  def stop(self):
    self.shutdown = True
    self.join()

  def run(self):
    while not self.shutdown:
      try:
        line = self.nano_ser.readline()
        if "Read: " in line:
          try:
            # Units are 1/100 oz
            val = float(line.replace("Read: ", "").rstrip()) / 100.0
            ts = time.time()
            with self.lock:
              self.buffer.append((ts, val))
            print val
          except ValueError:
            pass
        else:
          time.sleep(0.1)
      except TypeError:  # Happens if the read fails.
        pass
      except serial.SerialException:
        print "load cell serial exception"
        pass


class FakeLoadCellMonitor(LoadCellMonitor):
  def __init__(self, *args, **kwargs):
    self.random = random.Random()
    self.load_per_second = 0
    self.mean = 100.
    self.stddev = 2.
    self.last_read = time.time()
    self.sample_time_pct_var = .1
    super(FakeLoadCellMonitor, self).__init__(*args, adc=self, **kwargs)

  def readADCSingleEnded(self, _ch, _max, sample_rate):
    time.sleep(self.random.gauss(1., self.sample_time_pct_var) /
               sample_rate)  # sleep for the sample period
    sample_ts = time.time()
    self.mean += self.load_per_second * (sample_ts - self.last_read)
    self.last_read = sample_ts
    return self.random.gauss(self.mean, self.stddev)


def main():
  from math import sqrt
  monitor = LoadCellMonitor(bufsize=100000)
  while True:
    time.sleep(1)
    recent = monitor.recent_summary(secs=0.1)
    n = len(recent.records)
    print "n=%i mean=%f stddev=%f" % (n, recent.mean, recent.stddev)


if __name__ == "__main__":
  main()
