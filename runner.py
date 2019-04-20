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
    temp_img = ref_image.getLuminance()
    xderiv = temp_img.derivative(True)
    yderiv = temp_img.derivative(False)

    for i in range(1, maxStrokeLength+1):

        # i'm not sure what the derivative(x_i-1, y_i-1) means...
        lcpx, lcpy = K.getLastControlPoint()
        gx, gy = (255 * xderiv.getPixel(lcpx, lcpy), 255 * yderiv.getPixel(lcpx, lcpy))

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

    
        K.addPointRadii(math.sqrt(gx**2 + gy**2)*brush_i)
        K.addPoint(xi, yi)
        K.addDir(delxi, delyi)

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

def paintStrokeTwo(x0, y0, R, rImage, canvas):
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
        pid = canvas.getPixel(x, y)

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

        if(x < 0 or y < 0 or x >= width or y >= height):
            return K

        K.addPoint(x, y)
        K.addDir(dx, dy)
        K.addPointRadii(math.sqrt(gx**2 + gy**2)*R)

    return K 

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

        ### loop through gridspace
        for row in range(grid, height, grid):
            for col in range(grid, width, grid):
                #Scan through the pixels in this range...
                # This represents M...
                rRange, cRange = (row-grid, row+grid), \
                                 (col-grid, col+grid)
                M = (cRange, rRange)
                
                euclid = calculateError(canvas, i_ri, M[1], M[0])
                areaError = np.sum(euclid)
                
                if(refresh or areaError > T):
                    max_xs = np.argmax(euclid, axis=1)

                    temp_ys = np.arange(len(max_xs))
                    val = np.argmax(euclid[temp_ys, max_xs])
                    #print(euclid)
                    #print(max_xs)
                    #print(temp_ys)
                    x_i = max_xs[val] + col-grid
                    y_i = temp_ys[val] + row-grid
                    #print(x_i, y_i)
                    strokes.append(paintStrokeTwo(x_i, y_i, b, source, canvas))
        refresh = False

        print('brush done..')
        while(len(strokes) > 0):
            pos = random.randint(0, len(strokes)-1)
            b = strokes.pop(pos)
            renderStroke(b, canvas)


        canvas.save('images_output/test/van_gogh_result_2_{:d}.png'.format(b.getRadius()))
        # exit(0)
    #print(strokes)

    # and now render the brushes :)

    #strokes.sort(reverse=True, key=lambda x: x.getRadius())

    #canvas.save('/home/andrew/Desktop/outs/img_'+str(pos*random.randint(0,3))+'.png')

def renderStroke(b, canvas):

    print('render')

    #xs, cs, minRadius = b.calculateCubic()
    #interp = b.getInterpolatedArray(minRadius)

    #ys = cs(xs)

    ps = b.points

    res_h, res_w = canvas.getResolution()

    #print(xs, ys, interp, minRadius)
    radii = np.array(b.pointStrokeRadii).astype(int)

    for i in range(len(radii)-1):
        r = radii[i]
        x_r = math.ceil(ps[i][0])
        y_r = math.ceil(ps[i][1])

        x_r_1 = math.ceil(ps[i+1][0])
        y_r_1 = math.ceil(ps[i+1][1])
        #print('yes')
        cv.circle(canvas.image, (x_r, y_r), r, b.getColor(), -1)
        cv.line(canvas.image, (x_r, y_r), (x_r_1, y_r_1), b.getColor(), r*2)

    return canvas

if(__name__ == "__main__"):
    #Load image
    img = im.Image()
    img.load('images/van_gogh.jpg')

    canvas = im.Image()
    canvas.load('images/van_gogh.jpg')
    canvas.image.fill(255)

    paint(img, canvas, bss, False)

    canvas.save('images_output/test/van_gogh_3_test.png')

