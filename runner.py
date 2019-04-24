import image as im
import renderable_image as ri
import video as vid
import sys

# if processing a video, use this function
def process_video(in_file_name, out_file_name, render_type, TV):
    video_to_render = vid.Video(in_file_name)
    video_to_render.render(out_file_name, render_type, TV)

# if processing an image, use this function
def processImage(in_file_name, out_file_name, render_type):
    source = im.Image()
    source.load(in_file_name)
    canvas = im.Image()
    canvas.load(in_file_name)
    canvas.fillCanvas()

    render_image = ri.RenderableImage(source, canvas)
    render_image.render(render_type)
    render_image.getDestination().save(out_file_name)

# parses the commandline arguments and returns them to main
def parseInput():
    input_name = ""
    output_name = ""
    is_video = False
    render_type = ""
    TV = 0.0
    
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
        elif sys.argv[i] == '-tv':
            if i+1 >= len(sys.argv):
                print('ERROR: Didn\'t specify tv value.')
                exit(1)
            if sys.argv[i+1][0] == '-':
                print('ERROR: Didn\'t specify tv valuee. Did you put a \'-\' at the beginning of the name?')
                exit(1)
            TV = float(sys.argv[i+1])
        else:
            print('ERROR: Unknown option', sys.argv[i], 'specified.')
            exit(1)

    if input_name == "" or render_type == "":
        print('ERROR: file name not specified and/or render type not specified')
        exit(1)

    if output_name == "":
        output_name = "output.png"

    return (input_name, is_video, render_type, output_name, TV)
    
if(__name__ == "__main__"):
    input_name, is_video, render_type, output_name, TV = parseInput()
        
    if is_video:
        process_video(input_name, output_name, render_type, TV)
    else:
        processImage(input_name, output_name, render_type)

