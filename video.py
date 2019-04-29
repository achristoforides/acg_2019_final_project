import math
import random
import cv2 as cv
import numpy as np
import image as im
import brush_stroke as bs
import renderable_image as ri

# A wrapper class which is capable of producing an npr image
class Video:
    # constructor
    def __init__(self, in_file_name):
        self.renderable_images = []

        vidcap = cv.VideoCapture(in_file_name)
        success, img = vidcap.read()
        count = 0
        while success:
            src = im.Image()
            src.image = img
            dest = im.Image()
            dest.image = img
            dest.fillCanvas()

            self.renderable_images.append(ri.RenderableImage(src, dest))
            count += 1

            success, img = vidcap.read()

        print('video converted.')

    # Renders an npr video
    def render(self, out_file_name, style, TV):
        num_zeros = len(str(abs(len(self.renderable_images))))

        for z in range(len(self.renderable_images) - 1):
            self.renderable_images[z].render(style, TV, True)
            self.renderable_images[z].pinkCorrection()
            canvas = self.renderable_images[z].getDestination()

            file_path = out_file_name.split('/')
            file_path[-1] = str(z).zfill(num_zeros) + file_path[-1]
            
            canvas.save('/'.join(file_path))
            self.renderable_images[z+1].setDestination(canvas)
            print('Frame ' + str(z+1) + '/' + str(len(self.renderable_images)) + ' completed.')
            if z == len(self.renderable_images) - 2:
                self.renderable_images[z+1].render(style, TV, True)
                self.renderable_images[z+1].pinkCorrection()
                canvas = self.renderable_images[z+1].getDestination()

                file_path = out_file_name.split('/')
                file_path[-1] = str(z+1).zfill(num_zeros) + file_path[-1]
            
                canvas.save('/'.join(file_path))
                print('Frame ' + str(z+2) + '/' + str(len(self.renderable_images)) + ' completed.')
    
