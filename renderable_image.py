import math
import random
import cv2 as cv
import numpy as np
from image import Image
import brush_stroke as bs

f_sigma = 0.5
bss = [ 8, 4, 2]
T = 100
TV = 300
maxStrokeLength = 16
minStrokeLength = 4
f_c = 1

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
    def render(self, is_video = False):
        self.paint(bss, is_video)
        self.pinkCorrection()

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

    def pinkCorrection(self):
        height, width = self.dest.getResolution()

        for i in range(height):
            for q in range(width):
                aboveY = i+1
                rightX = q+1
                leftX = q-1
                belowY = i-1

                s = np.array([0,0,0]).astype(np.float64)
            
                currentPixel = self.dest.getPixel(q, i)

                if(currentPixel[0] == 255 and currentPixel[1] == 0 and currentPixel[2] == 255):
                    valid = 0
                    if(self.dest.inBounds(q, aboveY)):
                        p = self.dest.getPixel(q, aboveY)
                        if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                            s += p
                            valid+=1
                        
                    if(self.dest.inBounds(q, belowY)):
                        p = self.dest.getPixel(q, belowY)
                        if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                            s += p
                            valid+=1

                    if(self.dest.inBounds(rightX, i)):
                        p = self.dest.getPixel(rightX, i)
                        if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                            s += p
                            valid+=1

                    if(self.dest.inBounds(leftX, i)):
                        p = self.dest.getPixel(leftX, i)  
                        if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                            s += p
                            valid+=1

                    if(valid != 0):
                        s /= np.array([valid, valid, valid])
                        self.dest.setPixel(q, i, s)

    def getRange(self, img, rBounds, cBounds):
        return img.image[rBounds[0]:rBounds[1], cBounds[0]:cBounds[1]]

    def calculateError(self, ir, rBounds, cBounds):
        img1 = self.dest
        img2 = ir
        #Get kernel
        img1_block = self.getRange(img1, rBounds, cBounds)
        img2_block = self.getRange(img2, rBounds, cBounds)

        #Get RGB values for euclidean distance
        b1,g1,r1 = cv.split(img1_block)
        b2,g2,r2 = cv.split(img2_block)
        result = np.sqrt(np.power(r1-r2, 2) + np.power(g1-g2, 2) + np.power(b1-b2, 2))
        return result

    def paintStroke(self, x0, y0, R, rImage):
        color = rImage.getPixel(x0, y0)
        K = bs.BrushStroke(R, color)
        K.addPoint(x0, y0)
        K.addDir(0,0)
        K.addPointRadii(R)
        lastDx, lastDy = 0, 0
        x, y = x0, y0
        height, width = rImage.getResolution()
        temp_img = rImage.getLuminance()
        xderiv = temp_img.derivative(True)
        yderiv = temp_img.derivative(False)
        for i in range(1, maxStrokeLength+1):
            pir = rImage.getPixel(x, y)
            pid = self.dest.getPixel(x, y)

            pix_euc = math.sqrt( pow(pir[0]-pid[0], 2) + \
                                 pow(pir[1]-pid[1], 2) + \
                                 pow(pir[2]-pid[2], 2) )
            color_euc = math.sqrt( pow(pir[0]-color[0], 2) + \
                                   pow(pir[1]-color[1], 2) + \
                                   pow(pir[2]-color[2], 2) )

            if(i > minStrokeLength and pix_euc < color_euc):
                return K


            gx, gy = xderiv.getPixel(x, y), yderiv.getPixel(x, y)

            if(gx**2 + gy**2 == 0):
                return K

            dx, dy = -gy, gx

            if(lastDx * dx + lastDy * dy < 0):
                dx, dy = -dx, -dy

            dx, dy = f_c * dx + (1-f_c)*lastDx, f_c * dy + (1-f_c)*lastDy 
            dx, dy = dx / math.sqrt(dx**2 + dy**2), dy / math.sqrt(dx**2 + dy**2)

            x, y = x+R*dx , y+R*dy

            x, y = int(round(x)), int(round(y))

            lastDx, lastDy = dx, dy

            K.addPoint(x, y)
            K.addDir(dx, dy)
            K.addPointRadii(R)

            if(x < 0 or y < 0 or x >= width or y >= height):
                return K

        return K

    # Paint routine
    #
    # source:     Image, source image
    # canvas:     Image, resulting image
    # brushes:    list of brush radii
    # firstFrame: for video stuff
    def paint(self, brushes, firstFrame):
        strokes = []

        refresh = firstFrame
        brushes.sort(reverse = True)
        video = True if firstFrame else False
        for b in brushes:
            i_ri = self.source.gaussian(sigma=f_sigma, ksize=(int(f_sigma*b)-1, int(f_sigma*b)-1))
            grid = b

            height, width = self.source.getResolution()

            ### loop through gridspace
            for row in range(grid, height, grid):
                for col in range(grid, width, grid):
                    #Scan through the pixels in this range...
                    # This represents M...

                    rRange, cRange = (row-grid, row+grid), \
                                     (col-grid, col+grid)
                    M = (cRange, rRange)
                
                    euclid = self.calculateError(i_ri, M[1], M[0])

                    if(video):
                        diffError = self.calculateError(M[1], M[0])
                        videoError = np.sum(diffError)
                        thing = math.sqrt( ( M[0][0]-M[1][0] )**2 + ( M[0][1] - M[1][1] )**2 )
                        if thing == 0.0:
                            magnitude = 1
                        else:
                            magnitude = 1/(math.sqrt( ( M[0][0]-M[1][0] )**2 + ( M[0][1] - M[1][1] )**2 ))
                        
                        videoCheck = magnitude*videoError > TV
                    else:
                        videoCheck = True
                    areaError = np.sum(euclid)
                
                    if(refresh or (videoCheck and areaError > T)):
                        max_xs = np.argmax(euclid, axis=1)

                        temp_ys = np.arange(len(max_xs))
                        val = np.argmax(euclid[temp_ys, max_xs])
                        x_i = max_xs[val] + col-grid 
                        y_i = temp_ys[val] + row-grid 
                        strokes.append(self.paintStroke(x_i, y_i, b, i_ri))
                refresh = False

            print('brush done..')
            while(len(strokes) > 0):
                pos = random.randint(0, len(strokes)-1)
                stroke = strokes.pop(pos)
                self.renderStroke(stroke)

    def renderStroke(self, b):
        ps = b.points

        res_h, res_w = self.dest.getResolution()

        radii = np.array(b.pointStrokeRadii).astype(int)

        if(len(radii) == 1):
            r = radii[0]
            x_r = math.ceil(ps[0][0])
            y_r = math.ceil(ps[0][1])
            cv.circle(self.dest.image, (x_r, y_r), r, b.getColor(), -1)

        for i in range(len(radii)-1):
            r = radii[i]
            x_r = math.ceil(ps[i][0])
            y_r = math.ceil(ps[i][1])
            
            x_r_1 = math.ceil(ps[i+1][0])
            y_r_1 = math.ceil(ps[i+1][1])
            cv.circle(self.dest.image, (x_r, y_r), r, b.getColor(), -1)
            cv.line(self.dest.image, (x_r_1, y_r_1), (x_r, y_r), b.getColor(), r*2)

