# A wrapper class to hold all data which comprises a brush stroke
class BrushStroke:
    # radius : positive, floating point number
    def __init__(self, radius = 0):
        if radius < 0.0:
            self.radius = 0.0
            return
        self.radius = radius

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
