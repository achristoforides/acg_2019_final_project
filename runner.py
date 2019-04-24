import cv2 as cv
import math
import random
import image as im
import numpy as np
import renderable_image as ri
import brush_stroke as bs
import sys
import os

f_sigma = 0.5
bss = [ 8, 4, 2]
T = 100
TV = 300
maxStrokeLength = 16
minStrokeLength = 4
f_c = 1

def pinkCorrection(img_to_correct):
    height, width = img_to_correct.getResolution()

    for i in range(height):
        for q in range(width):
            aboveY = i+1
            rightX = q+1
            leftX = q-1
            belowY = i-1

            s = np.array([0,0,0]).astype(np.float64)
            
            currentPixel = img_to_correct.getPixel(q, i)

            if(currentPixel[0] == 255 and currentPixel[1] == 0 and currentPixel[2] == 255):
                valid = 0
                if(img_to_correct.inBounds(q, aboveY)):
                    p = img_to_correct.getPixel(q, aboveY)
                    if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                        s += p
                        valid+=1
                        
                if(img_to_correct.inBounds(q, belowY)):
                    p = img_to_correct.getPixel(q, belowY)
                    if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                        s += p
                        valid+=1

                if(img_to_correct.inBounds(rightX, i)):
                    p = img_to_correct.getPixel(rightX, i)
                    if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                        s += p
                        valid+=1

                if(img_to_correct.inBounds(leftX, i)):
                    p = img_to_correct.getPixel(leftX, i)  
                    if(p[0] != 255 or p[1] != 0 or p[2] != 255):
                        s += p
                        valid+=1

                if(valid != 0):
                    s /= np.array([valid, valid, valid])
                    img_to_correct.setPixel(q, i, s)

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

def paintStroke(x0, y0, R, rImage, canvas):
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
    video = True if firstFrame else False
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

                if(video):
                    diffError = calculateError(canvas, source, M[1], M[0])
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
                    strokes.append(paintStroke(x_i, y_i, b, i_ri, canvas))
        refresh = False

        print('brush done..')
        while(len(strokes) > 0):
            pos = random.randint(0, len(strokes)-1)
            b = strokes.pop(pos)
            renderStroke(b, canvas)

def renderStroke(b, canvas):

    ps = b.points

    res_h, res_w = canvas.getResolution()

    radii = np.array(b.pointStrokeRadii).astype(int)

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
        cv.circle(canvas.image, (x_r, y_r), r, b.getColor(), -1)
        cv.line(canvas.image, (x_r_1, y_r_1), (x_r, y_r), b.getColor(), r*2)

    return canvas

def process_video(in_file_name, out_file_name):
    srcs = []
    dests = []

    vidcap = cv.VideoCapture(in_file_name)
    success,image = vidcap.read()
    count = 0
    while success:
        src = im.Image()
        src.image = image
        height, width = src.getResolution()
        dest = im.blankCanvas(width, height)

        srcs.append(src)
        dests.append(dest)

        success,image = vidcap.read()

    print('video converted.')

    num_zeros = len(str(abs(len(srcs))))

    for z in range(len(srcs) - 1):
        paint(srcs[z], dests[z], bss, False)
        canvas = dests[z]
        
        pinkCorrection(canvas)
                        
        canvas.save(str(z).zfill(num_zeros) + out_file_name)
        dests[z+1].image = canvas.image
        print('Frame ' + str(z+1) + '/' + str(len(srcs)) + ' completed.')
        if z == len(srcs) - 2:
            paint(srcs[z+1], dests[z+1], bss, False)
            canvas = dests[z+1]

            pinkCorrection(canvas)

            canvas.save(str(z+1).zfill(num_zeros) + out_file_name)
            print('Frame ' + str(z+2) + '/' + str(len(srcs)) + ' completed.')

def processImage(in_file_name, out_file_name):
    source = im.Image()
    source.load(in_file_name)
    canvas = im.Image()
    canvas.load(in_file_name)
    canvas.fillCanvas()

    paint(source, canvas, bss, False)

    pinkCorrection(canvas)

    canvas.save(out_file_name)

def parseInput():
    input_name = ""
    output_name = ""
    is_video = False
    render_type = ""
    
    if len(sys.argv) < 3:
        print('ERROR: Incorrect Usage...')
        print('Example: python runner.py -[image/video] file_name -style rendering_style', \
              '[-output output_name]')
        exit(0)

    for i in range(1, len(sys.argv), 2):
        if sys.argv[i] == "-image":
            is_video = False
            if i+1 >= len(sys.argv):
                print('ERROR: Didn\'t specify input image name.')
                exit(1)
            if sys.argv[i+1][0] == '-':
                print('ERROR: Didn\'t specify input image name. Did you put a \'-\' at the beginning of the name?')
                exit(1)
            input_name = sys.argv[i+1]
        elif sys.argv[i] == "-video":
            is_video = True
            if i+1 >= len(sys.argv):
                print('ERROR: Didn\'t specify input video name.')
                exit(1)
            if sys.argv[i+1][0] == '-':
                print('ERROR: Didn\'t specify input video name. Did you put a \'-\' at the beginning of the name?')
                exit(1)
            input_name = sys.argv[i+1]
        elif sys.argv[i] == "-style":
            if i+1 >= len(sys.argv):
                print('ERROR: Didn\'t specify rendering style.')
                exit(1)
            if sys.argv[i+1][0] == '-':
                print('ERROR: Didn\'t specify rendering style. Did you put a \'-\' at the beginning of the name?')
                exit(1)
            render_type = sys.argv[i+1]
        elif sys.argv[i] == '-output':
            if i+1 >= len(sys.argv):
                print('ERROR: Didn\'t specify output name.')
                exit(1)
            if sys.argv[i+1][0] == '-':
                print('ERROR: Didn\'t specify output name. Did you put a \'-\' at the beginning of the name?')
                exit(1)
            output_name = sys.argv[i+1]
        else:
            print('ERROR: Unknown option', sys.argv[i], 'specified.')
            exit(1)

    if input_name == "" or render_type == "":
        print('ERROR: file name not specified and/or render type not specified')
        exit(1)

    if output_name == "":
        output_name = "output.png"

    return (input_name, is_video, render_type, output_name)
    
if(__name__ == "__main__"):
    input_name, is_video, render_type, output_name = parseInput()
        
    if is_video:
        process_video(input_name, output_name)
    else:
        processImage(input_name, output_name)

