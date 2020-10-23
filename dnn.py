import aditofpython as tof
import numpy as np
import cv2 as cv
import argparse
from enum import Enum
import sys
import explorerhat as eh
import time

#Functions that make the robot turn around its axis
def turn_left():
    eh.motor.one.speed(speed)
    time.sleep(0.1)
    eh.motor.two.speed(-speed)

def turn_right():
    eh.motor.one.speed(-speed)
    time.sleep(0.1)
    eh.motor.two.speed(speed)


speed = 20
inWidth = 300
inHeight = 300
WHRatio = inWidth / float(inHeight)
inScaleFactor = 0.007843
meanVal = 127.5
thr = 0.2
WINDOW_NAME = "Display Objects"
WINDOW_NAME_DEPTH = "Display Objects Depth"


class ModesEnum(Enum):
    MODE_NEAR = 0
    MODE_MEDIUM = 1
    MODE_FAR = 2


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Script to run MobileNet-SSD object detection network ')
    parser.add_argument("--prototxt", default="MobileNetSSD_deploy.prototxt",
                        help='Path to text network file: '
                             'MobileNetSSD_deploy.prototxt')
    parser.add_argument("--weights", default="MobileNetSSD_deploy.caffemodel",
                        help='Path to weights: '
                             'MobileNetSSD_deploy.caffemodel')
    args = parser.parse_args()
    try:
        net = cv.dnn.readNetFromCaffe(args.prototxt, args.weights)
    except:
        print("Error: Please give the correct location of the prototxt and caffemodel")
        sys.exit(1)

    swapRB = False

    system = tof.System()
    status = system.initialize()
    if not status:
        print("system.initialize() failed with status: ", status)
    #Initialising the camera
    cameras = []
    status = system.getCameraList(cameras)
    if not status:
        print("system.getCameraList() failed with status: ", status)

    modes = []
    status = cameras[0].getAvailableModes(modes)
    if not status:
        print("system.getAvailableModes() failed with status: ", status)

    types = []
    status = cameras[0].getAvailableFrameTypes(types)
    if not status:
        print("system.getAvailableFrameTypes() failed with status: ", status)

    status = cameras[0].initialize()
    if not status:
        print("cameras[0].initialize() failed with status: ", status)

    status = cameras[0].setFrameType(types[0])
    if not status:
        print("cameras[0].setFrameType() failed with status:", status)

    status = cameras[0].setMode(modes[ModesEnum.MODE_NEAR.value])
    if not status:
        print("cameras[0].setMode() failed with status: ", status)

    camDetails = tof.CameraDetails()
    status = cameras[0].getDetails(camDetails)
    if not status:
        print("system.getDetails() failed with status: ", status)

    # Enable noise reduction for better results
    smallSignalThreshold = 100
    cameras[0].setControl("noise_reduction_threshold", str(smallSignalThreshold))

    camera_range = camDetails.maxDepth
    bitCount = camDetails.bitCount
    frame = tof.Frame()

    max_value_of_IR_pixel = 2 ** bitCount - 1
    distance_scale_ir = 255.0 / max_value_of_IR_pixel
    distance_scale = 255.0 / camera_range
    
    #Mediating the distance between frames
    s=0
    c=0
    fps=10
    #eh.motor.forwards()
    
    ##############################
    ### ONE FRAME TEST ###
    
     # Capture frame-by-frame
    status = cameras[0].requestFrame(frame)
    if not status:
        print("cameras[0].requestFrame() failed with status: ", status)

    depth_map = np.array(frame.getData(tof.FrameDataType.Depth), dtype="uint16", copy=False)
    
    # Creation of the Depth image
    new_shape = (int(depth_map.shape[0] / 2), depth_map.shape[1])
    depth_map = cv.flip(depth_map, 1)
    distance_map = depth_map
    depth_map = distance_scale * depth_map
    depth_map = np.uint8(depth_map)
    depth_map = cv.applyColorMap(depth_map, cv.COLORMAP_RAINBOW)
    
    h = 480
    w = 640
    aux = [[0 for i in range(w)] for j in range(h)]
    
           

    d_lim = 500
   
    s=s+int(distance_map[240,320])
    
    for i in range(h-20):
        for j in range(w-20):
            if distance_map[i][j]>d_lim:
                aux[i][j]=' '
            else:
                aux[i][j] = '*'
    
    f = open('data.txt', 'w')
    

    linmin = 120 #160
    colmin = 160 #213
    linmax = 360 #320
    colmax = 480 #426
    
    for i in range(160, 321):
        for j in range(213, 427):
            f.write(str(aux[i][j])) 
        f.write('\n')
    
    value_x = 320
    value_y = 240
    cv.drawMarker(depth_map, (value_x, value_y), (0, 0, 0), cv.MARKER_CROSS)
    
    #Show distance from the center pixel
    label_depth ="{0:.3f}".format(s / 1000) + "m"
    cv.putText(depth_map, label_depth, (320 ,  240 ),
               cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
   
        
    s=0

    f.close()
    # Show Depth map
    cv.namedWindow(WINDOW_NAME_DEPTH, cv.WINDOW_AUTOSIZE)
    cv.imshow(WINDOW_NAME_DEPTH, depth_map)

    
    ##############################
    '''
    while True:
        # Capture frame-by-frame
        status = cameras[0].requestFrame(frame)
        if not status:
            print("cameras[0].requestFrame() failed with status: ", status)

        depth_map = np.array(frame.getData(tof.FrameDataType.Depth), dtype="uint16", copy=False)
        
        # Creation of the Depth image
        new_shape = (int(depth_map.shape[0] / 2), depth_map.shape[1])
        depth_map = cv.flip(depth_map, 1)
        distance_map = depth_map
        depth_map = distance_scale * depth_map
        depth_map = np.uint8(depth_map)
        depth_map = cv.applyColorMap(depth_map, cv.COLORMAP_RAINBOW)
        
        h = 480
        w = 640
        aux = [[0 for i in range(480)] for j in range(640)]
        
               
        c=c+1
        s=s+int(distance_map[240,320])
        if c==fps :           
            for i in range(20):
                for j in range(20):
                    if distance_map[i][j]>d_lim:
                        aux[i][j] = 0
                    else:
                        aux[i][j] = 1
            
            for i in aux:
                for j in i:
                    print (j, end = ' ')
                print()
            
            
            s=s/fps
            print(s)
            
            if s<d_lim :
                eh.motor.stop()
                timp=0
                t_lim=2
                while distance_map[320,240]<d_lim and timp<t_lim:
                    turn_right()
                    time.sleep(1)
                    timp=timp+1
                    
                eh.motor.stop()
                time.sleep(1)
                t_lim=4
                timp=0
                while distance_map[320,240]<d_lim and timp<t_lim:
                    turn_left()
                    time.sleep(1)
                    timp=timp+1
                    
                eh.motor.stop()
                
            else :
                eh.motor.forwards()
            c=0
            #Making the cross
            value_x = 320
            value_y = 240
            cv.drawMarker(depth_map, (value_x, value_y), (0, 0, 0), cv.MARKER_CROSS)
            
            #Show distance from the center pixel
            label_depth ="{0:.3f}".format(s / 1000) + "m"
            cv.putText(depth_map, label_depth, (320 ,  240 ),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
           
                
            s=0

            
            # Show Depth map
            cv.namedWindow(WINDOW_NAME_DEPTH, cv.WINDOW_AUTOSIZE)
            cv.imshow(WINDOW_NAME_DEPTH, depth_map)
             

        if cv.waitKey(1) >= 0:
            print(aux)
            break
        '''  
        
        
        
