# gcodefile library
#
# A turtle-graphics like library for generating GCode scripts
# for a MakerBot-like 3D printer.
#
# derived from original code by MaskedRetreiver
# refactored a bit by jonathan.mayer@gmail.com
#
# relies on numpy

import sys
from Numeric import *

class GCodeFile:
  """GCodeFile - an interface for generating GCode

  Provides two interfaces with overlapping functionality:
     - an interface for moving the print head within the frame of reference
     - an interface for changing the frame of reference
  """

  def __init__(self, filename=None):
    self.filename = filename
    # set up the gcode file:
    if not filename:
      self.fd = sys.stdout
    else:
      self.fd = open(filename, "w")
    self.__PrintHeader()
    # position of the print head:
    self.xy = array((0.0, 0.0, 1.0))  # homogenous coordinates (x,y,1)
    self.step = 0  # integer indicating the z height in steps
    self.stepsize = 0.4  # converts steps to height
    self.f = 700.0
    self.transform_matrix = identity(3)  # affine, 2D rotation and offset

  def __PrintHeader(self):
    """Only invoked by the constructor."""
    self.fd.writelines((
      "G21\n",
      "G90\n",
      "M103\n",
      "M105\n",
      "M104 S220.0\n",
      "M101\n"))

  def XY(self):
    position = matrixmultiply(self.xy, self.transform_matrix)
    return position[:2]

  def Go(self):
    """Emit the G command to move the printhead to the new position."""
    position = self.XY()
    z = self.CurrentHeight()
    command = "G1 X%.2f Y%.2f Z%.2f F%s\n" % \
              (position[0], position[1], z, self.f)
    self.fd.write(command) 
    return self

  def Step(self, count=1):
    self.step += count
    return self

  def CurrentHeight(self):
    return self.step * self.stepsize

  def Set(self, x, y):
    self.xy[0] = x
    self.xy[1] = y
    return self

  def Move(self, x, y):
    self.xy[0] += x
    self.xy[1] += y
    return self

  def Rotate(self, theta):
    """Rotates counter-clockwise by theta."""
    rotmatrix = array(((math.cos(theta), -math.sin(theta)),
                       (math.sin(theta),  math.cos(theta))))
    self.xy[:2] = matrixmultiply(rotmatrix, self.xy[:2])
    return self

  def Snap(self, precision=2):
    self.xy = around(self.xy, precision)
    return self

  def FrameMove(self, x, y):
    move_op = identity(3)
    move_op[2,0] = -x
    move_op[2,1] = -y
    self.transform_matrix = matrixmultiply(self.transform_matrix, move_op)
    return self

  def FrameRotate(self, theta):
    rotmatrix = array(((math.cos(theta), -math.sin(theta), 0.0),
                       (math.sin(theta),  math.cos(theta), 0.0),
                       (0.0,             0.0,              1.0)))
    self.transform_matrix = matrixmultiply(self.transform_matrix, rotmatrix)
    return self

  def __PrintFooter(self):
    self.fd.writelines(("M103\n",))
    self.Step(10).Go()
    self.fd.writelines(("M104 S0\n",))

  def Close(self):
    self.__PrintFooter()
    if self.filename:
      # don't close stdout
      self.fd.close()
    return self
