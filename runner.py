import image as im
import renderable_image as ri
import brush_stroke as bs

if(__name__ == "__main__"):

    #Load image
    img = im.Image()
    img.load('images/van_gogh.jpg')

    g = img.gaussian()

    #Convert to grayscale before derivative
    g_img = img.getGrayScale()
    d = g_img.derivative()

    g.save('images_output/van_gogh_gaussian.jpg')

    d.save('images_output/van_gogh_derivative.jpg')
