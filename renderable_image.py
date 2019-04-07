from image import Image
from brush_stroke import BrushStroke

# A wrapper class which is capable of producing an npr image
class RenderableImage:

    # source : Image
    # dest   : Image
    def __init__(self, source = Image(), dest = Image()):
        self.source = source
        self.dest = dest

    # Renders an npr image based on the current source and dest images
    # and stores it in dest
    #
    # b     : list of Brushes
    # begin : boolean
    def render(b = [], begin = False):
        print("Render!")

    # Sets the source image for this RenderableImage
    #
    # img : Image
    def setSource(self, img):
        self.source = img

    # Returns the source image for this RenderableImage
    def getSource(self):
        return self.source

    # Returns the destination image for this RenderableImage
    def getDestination(self):
        return self.dest

    # Sets the destination image for this RenderableImage
    #
    # img : Image
    def setDestination(self, img):
        self.dest = img
