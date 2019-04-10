import image as im
import numpy as np
import renderable_image as ri
import brush_stroke as bs

f_sigma = 0
T = 0

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
                    #paintStroke(max_pos[0], max_pos[1], canvas, b, i_ri)
        refresh = False

if(__name__ == "__main__"):

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
