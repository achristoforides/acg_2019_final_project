import cv2 as cv
import numpy as np

 # An image wrapper class for OpenCV and numpy arrays
class Image:
   
    # image : np.ndarray()
    # np.ndarray([[],[]])):
    def __init__(self, image = np.array([[],[]], np.int32)):
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
    def load(self, path):
        if path == '' or path == None:
            return
        self.image = cv.imread(path, cv.IMREAD_COLOR)

    # Gets the specified pixel in the image, tuple (b, g, r), returns
    # None if an invalid pixel is specified
    def getPixel(self, x, y):
        resolution_x, resolution_y = self.getResolution()
        if x < 0 or y < 0 or x >= resolution_x or y >= resolution_y:
            return None
        return self.image[x, y]

    # Sets the value of the specified pixel in the image, takes in a
    # tuple in the form (b, g, r), if the specified pixel is invalid,
    # then nothing will happen
    def setPixel(self, x, y, v):
        resolution_x, resolution_y = self.getResolution()
        if x < 0 or y < 0 or x > resolution_x or y > resolution_y:
            return
        self.image[x, y] = v

    # Returns a tuple containing the resolution of the image (width, height)
    def getResolution(self):
        return (self.image.shape[0], self.image.shape[1])

    # Compute and return the derivative of the image
    def derivative(self):
        pass

    # Compute and return a gaussian blur for the image
    def gaussian(self):
        pass

        
