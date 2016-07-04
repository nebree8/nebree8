"""Code shared by tools."""

import sys

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import gflags
gflags.DEFINE_bool("fake", False, "Use fake")


def make_robot():
  if gflags.FLAGS.fake:
    from fake_robot import FakeRobot
    return FakeRobot()
  else:
    from physical_robot import PhysicalRobot
    return PhysicalRobot()


gflags.FLAGS(sys.argv)
