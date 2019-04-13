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

    for i in range(1, maxStrokeLength):
        temp_img = ref_image.getLuminance()
        xderiv = temp_img.derivative(True)
        yderiv = temp_img.derivative(False)

        # i'm not sure what the derivative(x_i-1, y_i-1) means...
        gx, gy = (255 * xderiv.getPixel(x0 + i - 1, y0 + i - 1), \
                  255 * yderiv.getPixel(x0 + i - 1, y0 + i - 1))

        gxm1, gym1 = (255 * xderiv.getPixel(x0 + i - 2, y0 + i - 2), \
                      255 * yderiv.getPixel(x0 + i - 2, y0 + i - 2))
        delxim1, delyim1 = (-gym1, gxm1)

        if brush_i * sqrt(gx*gx + gy*gy) >= 1:
            # rotate gradient by 90 degrees
            delxi, delyi = (-gy, gx)

            # reverse direction if necessary
            #  we need to access the delxi-1 and delyi-1?!?!?!
            if i > 1 and delxim1 * delxi + delyim1 * delyi < 0:
                delxi, delyi = (-delxi, -delyi)

            # filter stroke direction
            delxi, delyi = (f_c * delxi + (1 - f_c) * delxim1, \
                            f_c * delyi + (1 - f_c) * delyim1)

        else:
            if i > 1:
                delxi, delyi = (delxim1, delyim1)
            else:
                return K

        xi, yi = ((x0 + i - 1) + brush_i * (delxi) / sqrt(delxi*delxi + delyi*delyi), \
                  (y0 + i - 1) + brush_i * (delyi) / sqrt(delxi*delxi + delyi*delyi))

        color_sub = ref_image.getPixel(xi, yi) - ref_image.getPixel(xi, yi)
        img_euc = sqrt(color_sub[0]*color_sub[0] + color_sub[1]*color_sub[1] + color_sub[2]*color_sub[2])
        ref_color_sub = ref_image.getPixel(xi, yi) - color
        ref_color_euc = sqrt(ref_color_sub[0]*ref_color_sub[0] + ref_color_sub[1]*ref_color_sub[1] + \
                             ref_color_sub[2]*ref_color_sub[2])
        if i > minStrokeLength and img_euc < ref_color_euc:
            return K
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

def paint(source, canvas, brushes, firstFrame):
    refresh = firstFrame
    brushes.sort(reverse = True)
    for b in brushes:
        i_ri = source.getGaussian(kernel=f_sigma*b)
        grid = b
        space_calc_x = source.width / grid
        space_calc_y = source.height / grid

        ### loop through gridspace
        for row in range(space_calc_x):
            start_r = row * grid + grid
            for col in range(space_calc_y):
                start_c = col * grid + grid
                #Scan through the pixels in this range...
                # This represents M...
                rRange, cRange = (start_r-grid/2, start_r+grid/2), \
                                 (start_c-grid/2, start_c+grid/2)
                M = (rRange, cRange)
                euclid = calculateError(canvas, i_ri, M[0], M[1])
                areaError = np.sum(euclid)
                if(refresh or areaError > T):
                    max_pos = np.argmax(euclid, axis=1)
                    #paintStroke(max_pos[0][0], max_pos[0][1], canvas, b, i_ri)
        refresh = False

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
