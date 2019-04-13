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
