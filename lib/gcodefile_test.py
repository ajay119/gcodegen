#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Tests for gcodefile."""

import math
import gcodefile
import unittest
from Numeric import *

def square(v):
  return power(v, 2)

def norm(v):
  return sqrt(sum(square(v)))

class TestGCodeFile(unittest.TestCase):
  def setUp(self):
    self.d45 = math.pi / 4.0
    self.g = gcodefile.GCodeFile("/dev/null")

  def tearDown(self):
    self.g.Close()

  def testTranslation(self):
    # translation
    self.g.Move(1,0).Go()
    self.assertEqual(self.g.XY(), (1.0, 0.0))
    self.g.Move(1,0).Go()
    self.assertEqual(self.g.XY(), (2.0, 0.0))
    self.g.Move(0,-1).Go()
    self.assertEqual(self.g.XY(), (2.0, -1.0))

  def testRotation(self):
    # translation
    self.g.Move(2,0).Go()
    self.assertEqual(self.g.XY(), (2.0, 0.0))

    # rotation
    self.g.Rotate(self.d45).Go()
    self.g.Rotate(self.d45).Go()
    self.g.Snap()  # rounding error removed
    self.assertEqual(self.g.XY(), (0.0, 2.0))
    self.g.Rotate(self.d45).Go().Rotate(self.d45).Go()
    self.g.Snap()  # rounding error removed
    self.assertEqual(self.g.XY(), (-2.0, 0.0))
    self.g.Rotate(self.d45).Go().Rotate(self.d45).Go()
    self.g.Snap()  # rounding error removed
    self.assertEqual(self.g.XY(), (0.0, -2.0))

  def testFrameOffset(self):
    # translation
    self.g.Move(2,0).Go()
    self.assertEqual(self.g.XY(), (2.0, 0.0))

    self.g.FrameMove(0,1)
    self.assertEqual(self.g.XY(), (2.0, -1.0))

    self.g.FrameMove(0,5)
    self.assertEqual(self.g.XY(), (2.0, -6.0))

    self.g.FrameMove(1,0)
    self.assertEqual(self.g.XY(), (1.0, -6.0))

  def testFrameRotate(self):
    # translation
    self.g.Move(2,0).Go()
    self.assertEqual(self.g.XY(), (2.0, 0.0))

    self.g.FrameRotate(self.d45)
    self.g.FrameRotate(self.d45)
    delta = norm(self.g.XY() - array((0.0, -2.0)))
    self.assertAlmostEqual(delta, 0.0)

if __name__ == '__main__':
  unittest.main()
