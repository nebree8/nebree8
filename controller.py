#!/usr/bin/env python

import time
import threading
import collections
import logging
import os

from actions.action import ActionException
from actions.wait_for_glass_removal import WaitForGlassRemoval
from actions.move import Move

class Controller:
  def __init__(self, robot):
    self.current_action = None
    self.queue = collections.deque()
    self.queued_sem = threading.Semaphore(0)
    self.queue_lock = threading.Lock()
    self.resume_lock = threading.Lock()
    self.resume_lock.acquire()
    self.robot = robot
    self.last_exception = None
    self.__StartThread()
    self.app = None

  def __StartThread(self):
    thread = threading.Thread(target=self.__Process)
    thread.daemon = True
    thread.start()

  def __Process(self):
    while True:
      logging.info("Waiting for actions...")
      self.queued_sem.acquire() # Ensure there are items to process.
      with self.queue_lock:
        self.current_action = self.queue.popleft()
      try:
        if self.current_action.sensitive():
          self.app.drop_all = True
        logging.info("Executing %s", self.current_action.inspect())
        self.current_action(self.robot)
      except ActionException, e:
        self.last_exception = e
        logging.info("Waiting for resume signal...")
        self.resume_lock.acquire()
        logging.info("Resume signal received, continuing to process actions.")
      except Exception, e:
        threading.Thread(target=self.KillProcess).start()
        raise
      finally:
        self.current_action = None
        self.app.drop_all = False

  def EnqueueGroup(self, action_group):
    with self.queue_lock:
      for action in action_group:
        self.queue.append(action)
        # Signal that there are items to process.
        self.queued_sem.release() 
    self.WriteToFile()

  def WriteToFile(self):
    queue_contents = self.InspectQueue()
    name_and_drink_lines = []
    name_and_drink = []
    i = 0
    for action in queue_contents:
      if type(action) == WaitForGlassRemoval:
        creating_message = ""
        if i == 0:
          creating_message = " <===== ACTIVE"
        i += 1;
        name_and_drink.append((action.user_name, action.drink_name))
        name_and_drink_lines.append("%d.\tCreating %s a %s%s\n" %
            (i, action.user_name, action.drink_name, creating_message))
    name_and_drink_lines.append("\n\n\n Holding Pressure: %s" % self.robot.pressurized)
    queue_txt = open("/home/pi/nebree82/nebree8/monitor/data/queue.txt", "w")
    queue_txt.write("\n".join(name_and_drink_lines))
    queue_txt.close()

  def InspectQueue(self):
    with self.queue_lock:
      return (([self.current_action] if self.current_action else []) +
          list(self.queue))

  def KillProcess(self):
    time.sleep(1)
    os._exit(1)

  def __Resume(self):
    self.last_exception = None
    self.resume_lock.release()

  def ClearAndResume(self):
    print "Clearing queue"
    while self.queued_sem.acquire(False): pass
    self.queue.clear()
    self.__Resume()

  def SkipAndResume(self):
    self.__Resume()

  def Retry(self):
    print "Kicking off retry..."
    self.queue.appendleft(self.current_action)
    self.queued_sem.release()
    self.__Resume()
