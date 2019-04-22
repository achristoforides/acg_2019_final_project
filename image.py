import cv2 as cv
import numpy as np

 # An image wrapper class for OpenCV and numpy arrays
class Image:

    # image : np.ndarray()
    # np.ndarray([[],[]])):
    def __init__(self, image = np.array([[],[]], np.int64)):
        self.image = image

    # Saves the image at the specified path, if path is an empty string or
    # None, don't save the image to disk
    def save(self, path):
        if path == '' or path == None:
            return
        cv.imwrite(path, self.image)

    # Loads the image at the specified path into the image property, if
    # path is an empty string or None, don't modify the image currently
    # stored
    def load(self, path, isColor = True):
        if path == '' or path == None:
            return
        flag = cv.IMREAD_COLOR if isColor else cv.IMREAD_GRAYSCALE
        self.image = cv.imread(path, flag)

    # Gets the specified pixel in the image, tuple (b, g, r), returns
    # None if an invalid pixel is specified. The x and y parameter work as
    # in standard mathematics; x is position on the horizontal axis, and y
    # is position on the vertical axis
    def getPixel(self, x, y):
        resolution_y, resolution_x = self.getResolution()
        if x < 0 or y < 0 or x >= resolution_x or y >= resolution_y:
            return np.array([])
        return self.image[y, x].astype(np.float64)

    # Sets the value of the specified pixel in the image, takes in a
    # tuple in the form (b, g, r), if the specified pixel is invalid,
    # then nothing will happen. The x and y parameter work as in standard
    # mathematics; x is position on the horizontal axis, and y is position
    # on the vertical axis
    def setPixel(self, x, y, v):
        self.image[y, x] = v

    def inBounds(self, x, y):
        resolution_y, resolution_x = self.getResolution()
        if x < 0 or y < 0 or x >= resolution_x or y >= resolution_y:
            return False
        return True

    # Gets the grayscale image for this image
    def getGrayScale(self):
        return Image(cv.cvtColor(self.image, cv.COLOR_BGR2GRAY))

    def getLuminance(self):
        lumi = cv.cvtColor(self.image, cv.COLOR_BGR2YCrCb)
        result,_,_ = cv.split(lumi)
        r = cv.normalize(result, None, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=cv.CV_32F)
        return Image(r)

    # Returns a tuple containing the resolution of the image (width, height)
    def getResolution(self):
        return (self.image.shape[0], self.image.shape[1])

    # Compute and return the derivative of the image
    def derivative(self, isX):
        if(isX):
            return Image(cv.Sobel(self.image, cv.CV_64F, 1, 0))
        return Image(cv.Sobel(self.image, cv.CV_64F, 0, 1))

    # Compute and return a gaussian blur for the image
    def gaussian(self, ksize = None, sigma = None):
        if(sigma == None):
            sigma = 2
        if(ksize == None):
            ksize = (4*sigma+1,4*sigma+1)
        return Image(cv.GaussianBlur(self.image, ksize, sigma))

