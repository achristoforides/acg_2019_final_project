import cv2 as cv
import math
import random
import image as im
import numpy as np
import renderable_image as ri
import brush_stroke as bs
import sys
import os

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

    render_image = ri.RenderableImage(source, canvas)
    render_image.render()
    render_image.getDestination().save(out_file_name)

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

