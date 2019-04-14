import cv2 as cv
import math
import random
import image as im
import numpy as np
import renderable_image as ri
import brush_stroke as bs

f_sigma = 0.5
bss = [ 8, 4, 2]
T = 100
maxStrokeLength = 16
minStrokeLength = 4
f_c = 1

# PaintStroke routine
#
# x0:              int, starting x point
# y0:              int, starting y point
# brush_i:         float, brush radius
# ref_image:       Image, reference image
# painting_so_far: Image, current render of image
def paintStroke(x0, y0, brush_i, ref_image, painting_so_far):
    color = ref_image.getPixel(x0, y0)
    K = bs.BrushStroke(brush_i, color)
    K.addPoint(x0, y0)
    K.addDir(0, 0)
    K.addPointRadii(brush_i)

    for i in range(1, maxStrokeLength):
        temp_img = ref_image.getLuminance()
        xderiv = temp_img.derivative(True)
        yderiv = temp_img.derivative(False)

        # i'm not sure what the derivative(x_i-1, y_i-1) means...
        lcpx, lcpy = K.getLastControlPoint()
        gx, gy = (255 * xderiv.getPixel(lcpx, lcpy), 255 * yderiv.getPixel(lcpx, lcpy))

        if(not gx or not gy):
            continue

        ldx, ldy = K.getLastDirection()
        #print(brush_i, gx, gy)
        if brush_i * math.sqrt(gx*gx + gy*gy) >= 1:
            # rotate gradient by 90 degrees
            delxi, delyi = (-gy, gx)

            # reverse direction if necessary
            if i > 1 and ldx*delxi + ldy*delyi < 0:
                delxi, delyi = (-delxi, -delyi)

            # filter stroke direction
            delxi, delyi = (f_c * delxi + (1 - f_c) * ldx, f_c * delyi + (1 - f_c) * ldy)
        else:
            if i > 1:
                delxi, delyi = (ldx, ldy)
            else:
                return K

        if(delxi**2 == 0 or delyi**2 == 0):
            continue

        xi, yi = (math.ceil(lcpx + brush_i * (delxi) / math.sqrt(delxi*delxi + delyi*delyi)), \
                  math.ceil(lcpy + brush_i * (delyi) / math.sqrt(delxi*delxi + delyi*delyi)))

        pir = ref_image.getPixel(xi, yi)
        pid = painting_so_far.getPixel(xi, yi)

        if(len(pir) != 3 or len(pid) != 3):
            continue

        pix_euc = math.sqrt( pow(pir[0]-pid[0], 2) + \
                        pow(pir[1]-pid[1], 2) + \
                        pow(pir[2]-pid[2], 2) )
        color_euc = math.sqrt( pow(pir[0]-color[0], 2) + \
                          pow(pir[1]-color[1], 2) + \
                          pow(pir[2]-color[2], 2) )

        if i > minStrokeLength and pix_euc < color_euc:
            return K

        hit = False
        for i in K.points:
            if(i[0] == xi):
                hit = True
        if(not hit):
            K.addPointRadii(brush_i)
            K.addPoint(xi, yi)

    return K


def getRange(img, rBounds, cBounds):
    return img.image[rBounds[0]:rBounds[1], cBounds[0]:cBounds[1]]

def calculateError(img1, img2, rBounds, cBounds):
    #Get kernel
    img1_block = getRange(img1, rBounds, cBounds)
    img2_block = getRange(img2, rBounds, cBounds)

    #Get RGB values for euclidean distance
    b1,g1,r1 = cv.split(img1_block)
    b2,g2,r2 = cv.split(img2_block)
    result = np.sqrt(np.power(r1-r2, 2) + np.power(g1-g2, 2) + np.power(b1-b2, 2))
    return result

# Paint routine
#
# source:     Image, source image
# canvas:     Image, resulting image
# brushes:    list of brush radii
# firstFrame: for video stuff
def paint(source, canvas, brushes, firstFrame):
    strokes = []

    refresh = firstFrame
    brushes.sort(reverse = True)
    for b in brushes:
        i_ri = source.gaussian(sigma=f_sigma, ksize=(int(f_sigma*b)-1, int(f_sigma*b)-1))
        grid = b

        height, width = source.getResolution()
        space_calc_x = width // grid
        space_calc_y = height // grid

        ### loop through gridspace
        for row in range(space_calc_y):
            start_r = row * grid + grid
            for col in range(space_calc_x):
                start_c = col * grid + grid
                #Scan through the pixels in this range...
                # This represents M...
                rRange, cRange = (start_r-grid//2, start_r+grid//2), \
                                 (start_c-grid//2, start_c+grid//2)
                M = (cRange, rRange)
                try:
                    euclid = calculateError(canvas, i_ri, M[1], M[0])
                except:
                    continue
                    #print(euclid)
                areaError = np.sum(euclid)
                if(refresh or areaError > T):
                    max_ys = np.argmax(euclid, axis=1)
                    temp_xs = np.arange(len(max_ys))
                    val = np.argmax(euclid[temp_xs, max_ys])
                    x_i = temp_xs[val] + start_c-grid//2
                    y_i = max_ys[val] + start_r-grid//2
                    #print(x_i, y_i)
                    strokes.append(paintStroke(x_i, y_i, b, i_ri, canvas))
        refresh = False

        print('brush done..')
    #print(strokes)

    # and now render the brushes :)

    while(len(strokes) > 0):
        pos = random.randint(0, len(strokes)-1)
        b = strokes.pop(pos)
        if(len(b.points) >= 2):
            renderStroke(b, canvas)
            
            #canvas.save('/home/andrew/Desktop/outs/img_'+str(pos*random.randint(0,3))+'.png')

def renderStroke(b, canvas):

    print('render')

    xs, cs, minRadius = b.calculateCubic()
    interp = b.getInterpolatedArray(minRadius)

    ys = cs(xs)

    res_h, res_w = canvas.getResolution()

    #print(xs, ys, interp, minRadius)

    for x,y in zip(xs.astype(int), ys.astype(int)):
        x_r = math.ceil(x)
        r = 1
        y_r = math.ceil(y)
        if(x_r-r < 0 or x_r+r > res_w or y_r-r < 0 or y_r + r > res_h):
            #print('boooo')
            continue
        #print('yes')
        canvas.image[y_r-r:y_r+r, x_r-r:x_r+r] = b.getColor()

if(__name__ == "__main__"):
    #Load image
    img = im.Image()
    img.load('images/ig.png')

    canvas = im.Image()
    canvas.load('images/ig.png')
    canvas.image.fill(0)

    paint(img, canvas, bss, False)

    canvas.save('images_output/f9.png')

