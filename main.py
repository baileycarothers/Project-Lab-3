import cv2
import numpy as np
import math
import atexit
import threading
import time


from front_wheels import Front_Wheels as fw
from back_wheels import Back_Wheels
import hand_coded_lane_follower as hclf
from Servo import Servo
from rplidar import RPLidar 


stop_data = cv2.CascadeClassifier('stop_data.xml')

video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH,320)
video.set(cv2.CAP_PROP_FRAME_HEIGHT,240)

front = Servo(3)
front.setup()

bw = Back_Wheels()



lidar = RPLidar('/dev/ttyUSB0', baudrate=115200)
go = True



        
def lidarThread():
    global lidar
    global go
    while True:
        for measure in lidar.iter_scans():
            #print(measure)
            break
        for x in measure:
            if x[1] > 270 or x[1] < 90:
                if x[2] < 500 and x[2] > 0:
#                     print(x[2])
#                     print('STOP!!!')
                    go = False
                else:
                    go = True
t = threading.Thread(target=lidarThread)
t.start()

def killEverything():
    bw.stop()
    video.release()
    front.turn_straight()
    print("atexit successful")

signCount = 0
prevSA = 90
prev = 155
start = True
while True:
    if go:
        ret, frame = video.read()
        #Stop Sign detection
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        findSigns = stop_data.detectMultiScale(frame_gray, minSize =(50,50))
        signsFound = len(findSigns)
        
        if signsFound != 0:
            signCount += 1
        if signCount >= 2:
            print("Stop sign detected")
            go = False
            for (x,y,width,height) in findSigns:
                cv2.rectangle(frame, (x,y), (x + height, y + width), (0,255,0), 5)                 
                #v2.putText(frame, 'Stop Sign', (x-8,y-15), font, 1, (0,255,0), 4)
            signCount = 0
        #cv2.imshow('original', frame)
        edges = hclf.detect_edges(frame)
        roi = hclf.region_of_interest(edges)
        cv2.imshow("roi", roi)
        line_segments = hclf.detect_line_segments(roi)
        lane_lines = hclf.average_slope_intercept(frame,line_segments)
        lane_lines_image = hclf.display_lines(frame,lane_lines)
        steering_angle = hclf.compute_steering_angle(frame, lane_lines)
        print(steering_angle)
        heading_image = hclf.display_heading_line(lane_lines_image, steering_angle)
        #cv2.imshow("Webcam Feed",heading_image)
#         if abs(steering_angle-prevSA) > 40:
#             steering_angle = prevSA
        if steering_angle > 130:
            #turn right
            front.write(180)
            prev = 180
        elif steering_angle < 65 and steering_angle > 0:
            #turn left
            front.write(135)
            prev = 130
#         elif steering_angle < 0:
#             front.write(prev)
        else:
            #straight
            front.write(155)
        prevSA = steering_angle
        
        if cv2.waitKey(1) == ord('q'): #Press Q to quit
            break
        if start:
            bw.speed = 40
            bw.backward()
            start = False
        
    else:
#         continue
        bw.stop()
        time.sleep(3)
        bw.speed = 50
        bw.backward()
    
bw.stop()
video.release()
lidar.stop_motor()
lidar.stop()
 
lidar.disconnect()

atexit.register(killEverything)