import signal
import time
import Queue


class ScheduledEvent(object):
  def Execute(self):
    pass

  def GetNextTime(self, current_time):
    return 0


class AsyncQueue(object):
  def __init__(self):
    self.queue = Queue.PriorityQueue()
    signal.signal(signal.SIGALRM, self.HandleAlarm)

  def AddScheduledEvent(self, event):
    next_time = event.GetNextTime(time.time())
    if next_time > 0:
      self.queue.put((next_time, event))
    self.UpdateAlarm()

  def HandleAlarm(self, unused_signal, unused_frame):
    """Assumes the event on the top of the queue is ready. Executes it and
    updates the queue."""
    unused_time, next_event = self.queue.get()
    next_event.Execute()
    self.AddScheduledEvent(next_event)

  def UpdateAlarm(self):
    next_alarm_time, next_alarm_event = self.queue.get()
    self.queue.put((next_alarm_time, next_alarm_event))
    time_gap = next_alarm_time - time.time()
    try:
      signal.setitimer(signal.ITIMER_REAL, time_gap)
    except signal.ItimerError:
      print "Bad arg: %f, steps = %d" % (time_gap, next_alarm_event.steps)
      self.HandleAlarm(None, None)

# crap


class MotorUpdateEvent(async_queue.ScheduledEvent):
  def __init__(self,
               steps,
               io,
               motor,
               forward=1,
               ramp_seconds=0,
               final_wait=0.0002):
    self.steps = steps
    self.io = io
    self.motor = motor
    self.forward = forward
    self.ramp_seconds = ramp_seconds
    self.final_wait = final_wait

    self.io.WriteOutput(io_bank.Outputs.STEPPER_PULSE, 0)
    self.io.WriteOutput(io_bank.Outputs.STEPPER_DIR, forward)

    self.initial_wait = 0.002
    self.current_wait = self.initial_wait
    self.pulse_state = False

  def Execute(self):
    if self.forward:
      self.motor.colliding_negative = False
    else:
      self.motor.colliding_positive = False
    if not self.Complete():
      self.io.WriteOutput(io_bank.Outputs.STEPPER_PULSE, int(self.pulse_state))

      self.pulse_state = not self.pulse_state
      if self.steps > 600:
        if self.current_wait > self.final_wait:
          self.current_wait *= 0.996
      else:
        if self.current_wait < self.initial_wait:
          self.current_wait *= 1.004
      self.steps -= 1
    else:
      self.io.WriteOutput(io_bank.Outputs.STEPPER_PULSE, 0)
      print "Completed move."

  def GetNextTime(self, current_time):
    if not self.Complete():
      return current_time + self.current_wait

  def Complete(self):
    return (self.steps == 0 or
            (self.motor.colliding_positive and self.forward) or
            (self.motor.colliding_negative and not self.forward))
  # queue = async_queue.AsyncQueue()
  # queue.AddScheduledEvent(MotorUpdateEvent(steps, io, motor, forward))
