#!/usr/bin/python

import argparse
import sys
from parts import io_bank
from parts import motor


def main(args):
  parser = argparse.ArgumentParser(description='Move robot stepper motor.')
  parser.add_argument('--steps',
                      type=int,
                      nargs="?",
                      default=1,
                      help='Steps to move the motor')
  parser.add_argument('--inches',
                      type=float,
                      nargs="?",
                      default=0,
                      help='Inches to move the motor')
  parser.add_argument('--backward',
                      type=str,
                      nargs="?",
                      default="False",
                      help='Direction to move')
  parser.add_argument('--dry_run',
                      type=bool,
                      nargs="?",
                      default=False,
                      help='Whether to move motors')
  parser.add_argument('--positions',
                      type=float,
                      nargs="+",
                      default=(),
                      help='List of positions to move the truck through')
  parser.add_argument('--absolute',
                      type=bool,
                      nargs="?",
                      default=False,
                      help='Whether calibrate position')
  args = parser.parse_args()
  print args
  # For the NEMA 14 12v 350mA (#324) stepper motors from AdaFruit:
  # http://www.adafruit.com/products/324
  # Driving it with 12v using a delay of 1 microsecond.
  #Setup()
  io = io_bank.IOBank(update_shift_reg=False, update_arduino=False)
  stepper = motor.StepperMotor(dry_run=args.dry_run, io=io)
  rail = motor.RobotRail(stepper)
  if args.positions:
    if args.absolute:
      rail.CalibrateToZero()
    rail.FillPositions(args.positions)
    gpio.cleanup()
    return
  forward = (args.backward != "True")
  if args.inches:
    steps = motor.InchesToSteps(args.inches)
  else:
    steps = args.steps
  if forward:
    print "Forward %d steps" % steps
  else:
    print "Backward %d steps" % steps
  stepper.Move(steps, forward=forward)
  #gpio.cleanup()


if __name__ == "__main__":
  main(sys.argv)
