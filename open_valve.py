#!/usr/bin/env python
import time                                 
                                            
from physical_robot import PhysicalRobot    
                                            
VALVE=30
robot = PhysicalRobot()                     
with robot.OpenValve(VALVE):                
  time.sleep(.1) 
