import image as im
import numpy as np
import renderable_image as ri
import brush_stroke as bs

f_sigma = 0
T = 0
maxStrokeLength = 10
minStrokeLength = 2
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

        ldx, ldy = K.getLastDirection()
        if brush_i * sqrt(gx*gx + gy*gy) >= 1:
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

        xi, yi = (lcpx + brush_i * (delxi) / sqrt(delxi*delxi + delyi*delyi), \
                  lcpy + brush_i * (delyi) / sqrt(delxi*delxi + delyi*delyi))

        pir = ref_image.getPixel(xi, yi)
        pid = painting_so_far.getPixel(xi, yi)

        pix_euc = sqrt( pow(pir[0]-pid[0], 2) + \
                        pow(pir[1]-pid[1], 2) + \
                        pow(pir[2]-pid[2], 2) )
        color_euc = sqrt( pow(pir[0]-color[0], 2) + \
                          pow(pir[1]-color[1], 2) + \
                          pow(pir[2]-color[2], 2) )

        if i > minStrokeLength and pix_euc < color_euc:
            return K

        K.addPointRadii(brush_i * sqrt(gx*gx + gy*gy))
        K.addPoint(xi, yi)

    return K
                

def getRange(img, rBounds, cBounds):
    return img[rBounds[0]:rBounds[1], cBounds[0]:cBounds[1]]

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
        i_ri = source.getGaussian(kernel=f_sigma*b)
        grid = b

        width, height = source.getResolution()
        space_calc_x = width / grid
        space_calc_y = height / grid

        ### loop through gridspace
        for row in range(space_calc_y):
            start_r = row * grid + grid
            for col in range(space_calc_x):
                start_c = col * grid + grid
                #Scan through the pixels in this range...
                # This represents M...
                rRange, cRange = (start_r-grid/2, start_r+grid/2), \
                                 (start_c-grid/2, start_c+grid/2)
                M = (cRange, rRange)
                euclid = calculateError(canvas, i_ri, M[1], M[0])
                areaError = np.sum(euclid)
                if(refresh or areaError > T):
                    max_pos = np.argmax(euclid, axis=1)
                    strokes.append(paintStroke(max_pos[0][0], max_pos[0][1], b, i_ri, canvas))
        refresh = False

    # and now render the brushes :)

if(__name__ == "__main__"):
    #Pixel set test
    img = im.Image()
    img.load('images/van_gogh.jpg')

    img.setPixel(0, 0, (255, 0, 0))
    img.setPixel(1, 0, (0, 255, 0))
    img.setPixel(0, 1, (0, 0, 255))
    img.save('images_output/van_gogh.png')
    
    #Load image
    img = im.Image()
    img.load('images/whistler.png')

    g = img.gaussian()

    #Convert to grayscale before derivative
    g_img = img.getGrayScale()

    l_img = img.getLuminance()

    d_x = g_img.derivative(True)
    d_y = g_img.derivative(False)

    g.save('images_output/whistle_gaussian.png')

    #d_x.image = np.multiply(d_x.image, 255.0).astype(np.float)
    #d_y.image = np.multiply(d_y.image, 255.0).astype(np.float)
    #print(d_x.image)

    d_x.save('images_output/whistle_derivative_x.png')
    d_y.save('images_output/whistle_derivative_y.png')

    l_img.save('images_output/whistle_2.png')

    print(l_img.image)

    print(d_x.image)
    print(d_y.image)
