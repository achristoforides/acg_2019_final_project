import cv2 as cv
import math
import random
import image as im
import numpy as np
import renderable_image as ri
import brush_stroke as bs

f_sigma = 0.5
bss = [ 64, 32, 16, 4, 2]
T = 100
maxStrokeLength = 0
minStrokeLength = 0
f_c = 1

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
                    strokes.append(paintStrokeTwo(x_i, y_i, b, i_ri, canvas))
        refresh = False

        print('brush done..')
        while(len(strokes) > 0):
            pos = random.randint(0, len(strokes)-1)
            b = strokes.pop(pos)
            renderStroke(b, canvas)


        canvas.save('images_output/pink/ig_2_{:d}_point.png'.format(b.getRadius()))
        # exit(0)
    #print(strokes)

    # and now render the brushes :)

    #strokes.sort(reverse=True, key=lambda x: x.getRadius())

    #canvas.save('/home/andrew/Desktop/outs/img_'+str(pos*random.randint(0,3))+'.png')

def renderStroke(b, canvas):

    ps = b.points

    #radii = b.getInterpolatedArray()

    res_h, res_w = canvas.getResolution()

    #print(xs, ys, interp, minRadius)
    radii = np.array(b.pointStrokeRadii).astype(int)

    #print(radii)

    if(len(radii) == 1):
        r = radii[0]
        x_r = math.ceil(ps[0][0])
        y_r = math.ceil(ps[0][1])
        cv.circle(canvas.image, (x_r, y_r), r, b.getColor(), -1)

    for i in range(len(radii)-1):
        r = radii[i]
        x_r = math.ceil(ps[i][0])
        y_r = math.ceil(ps[i][1])

        x_r_1 = math.ceil(ps[i+1][0])
        y_r_1 = math.ceil(ps[i+1][1])
        #print('yes')
        cv.circle(canvas.image, (x_r, y_r), r, b.getColor(), -1)
        cv.line(canvas.image, (x_r_1, y_r_1), (x_r, y_r), b.getColor(), r*2)

    return canvas

if(__name__ == "__main__"):
    #Load image
    img = im.Image()
    img.load('images/liz.jpg')

    canvas = im.Image()
    canvas.load('images/liz.jpg')

    #this is me being lazy...
    b,g,r = cv.split(canvas.image)
    b.fill(255)
    g.fill(0)
    r.fill(255)

    canvas.image = cv.merge((b,g,r))

    paint(img, canvas, bss, False)

    height, width = canvas.getResolution()

    for i in range(height):
        for q in range(width):
            aboveY = i+1
            rightX = q+1
            leftX = q-1
            belowY = i-1

            s = np.array([0,0,0]).astype(np.float64)

            currentPixel = canvas.getPixel(q, i)


            if(currentPixel[0] == 255 and currentPixel[1] == 0 and currentPixel[2] == 255):
                #print(currentPixel)
                valid = 0
                if(canvas.inBounds(q, aboveY)):
                    p = canvas.getPixel(q, aboveY)
                    if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                        s += p
                        valid+=1

                if(canvas.inBounds(q, belowY)):
                    p = canvas.getPixel(q, belowY)
                    if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                        s += p
                        valid+=1
                    

                if(canvas.inBounds(rightX, i)):
                    p = canvas.getPixel(rightX, i)
                    if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                        s += p
                        valid+=1

                if(canvas.inBounds(leftX, i)):
                    p = canvas.getPixel(leftX, i)  
                    if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                        s += p
                        valid+=1

                if(valid != 0):
                    s /= np.array([valid, valid, valid])
                    canvas.setPixel(q, i, s)


    canvas.save('images_output/pink/ig_2_result_point.png')

