import math
import numpy as np
from scipy.interpolate import CubicSpline

# A wrapper class to hold all data which comprises a brush stroke
#
# radius: the radius of the brush
# color:  the color of the stroke
# points: the points added to the stroke, stores tuples (x, y)
class BrushStroke:
    # radius : positive, floating point number
    def __init__(self, radius = 0, color = (0, 0, 0)):
        if radius < 0.0:
            self.radius = 0.0
            return
        self.radius = radius
        self.color = color
        self.points = []
        self.dirs = []
        self.pointStrokeRadii = []
        self.spline = None
        self.npr = None

    # Returns the current radius of the BrushStroke
    def getRadius(self):
        return self.radius

    # Sets the radius of the current BrushStroke to the parameter passed
    # in, if r is negative, then radius is set to 0
    def setRadius(self, r = 0):
        if r < 0.0:
            self.radius = 0.0
            return
        self.radius = r

    # Returns the current color of the BrushStroke
    def getColor(self):
        return self.color

    # Sets the color of the current BrushStroke to the parameter passed
    # in, color should be a 3D tuple in the following format: (B, G, R)
    def setColor(self, color):
        self.color = color

    # Adds the specified (x, y) point to the points list
    def addPoint(self, x, y):
        self.points.append((x, y))

    def addDir(self, x, y):
        self.dirs.append((x, y))

    def addPointRadii(self, radii):
        self.pointStrokeRadii.append(radii)

    # Returns the last control point
    def getLastControlPoint(self):
        return self.points[-1]

    def getLastDirection(self):
        return self.dirs[-1]

    def getPointRadii(self, index):
        return self.pointStrokeRadii[index]

    def calculateCubic(self):
        start_x = self.points[0][0]
        start_y = self.points[0][1]

        end_x = self.points[-1][0]
        end_y = self.points[-1][1]

        #nprint("START END " , start_x, end_x)
        self.npr = np.arange(start_x, end_x, self.pointStrokeRadii[0])

        xs = []
        ys = []

        #print(self.points)

        for i in self.points:
            xs.append(i[0])
            ys.append(i[1])

        if(xs[0] > xs[-1]):
            self.pointStrokeRadii.reverse()
            self.npr = np.arange(end_x, start_x, 1)
            xs.reverse()
            ys.reverse()
            self.points.reverse()
        xs = np.array(xs)
        ys = np.array(ys)
        #print(xs, ys)
        #print(self.npr)
        self.spline = CubicSpline(xs, ys)
        #print(self.pointStrokeRadii)
        return (self.npr, self.spline, 1)

    def getInterpolatedArray(self):
        result = [0]*len(self.pointStrokeRadii) 
        return [math.ceil(self.pointStrokeRadii[i]-(i*self.pointStrokeRadii[i])/len(self.pointStrokeRadii)) for i in range(len(self.pointStrokeRadii)) ]

