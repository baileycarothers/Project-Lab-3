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



#lidar = RPLidar('/dev/ttyUSB0', baudrate=115200)
go = True



        
# def lidarThread():
#     global lidar
#     global go
#     while True:
#         for measure in lidar.iter_scans():
#             #print(measure)
#             break
#         for x in measure:
#             if x[1] > 270 or x[1] < 90:
#                 if x[2] < 500 and x[2] > 0:
#                     print(x[2])
#                     print('STOP!!!')
#                     go = False
#                 else:
#                     go = True
# t = threading.Thread(target=lidarThread)
# t.start()
# 
def killEverything():
    bw.stop()
    video.release()
    front.turn_straight()
    print("atexit successful")

num_of_lane_lines = 2
signCount = 0
prevSA = 90
prev = 155
curr_stabilized_steer = 90
start = True
while True:
    if go:
        ret, frame = video.read()
        #Stop Sign detection
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        findSigns = stop_data.detectMultiScale(frame_gray, minSize =(30,30))
        signsFound = len(findSigns)
        
        if signsFound != 0:
            signCount += 1
        if signCount >= 5:
            print("Stop sign detected")
            go = False
            for (x,y,width,height) in findSigns:
                cv2.rectangle(frame, (x,y), (x + height, y + width), (0,255,0), 5)                 
                #v2.putText(frame, 'Stop Sign', (x-8,y-15), font, 1, (0,255,0), 4)
            signCount = 0
        
        
        edges = hclf.detect_edges(frame)
        roi = hclf.region_of_interest(edges)
        line_segments = hclf.detect_line_segments(roi)
        lane_lines = hclf.average_slope_intercept(frame,line_segments)
        new_stabilized_steer = hclf.compute_steering_angle(frame, lane_lines)
        stabilized_steer = hclf.stabilize_steering_angle(curr_stabilized_steer, new_stabilized_steer, num_of_lane_lines, max_angle_deviation_two_lines=20, max_angle_deviation_one_lane=1)
        curr_stabilized_steer = stabilized_steer
        #stabilized_steer = new_stabilized_steer
        #print(stabilized_steer)
            
        #cv2.imshow('original', frame)
        #cv2.imshow("roi", roi)
        
        lane_lines_image = hclf.display_lines(frame,lane_lines)
        heading_image = hclf.display_heading_line(lane_lines_image, stabilized_steer)
        cv2.imshow("Webcam Feed",heading_image)

        if stabilized_steer < 0:
            #REVERSE
            print("first stop")
            front.write(155)
            bw.speed = 50
            bw.forward()
            time.sleep(0.05)
        elif stabilized_steer >= 80 and stabilized_steer <= 100:
            #straight
            print("straight")
            front.write(155)
            bw.speed = 50
            bw.backward()
        elif stabilized_steer > 100 and stabilized_steer < 150:
            #turn right
            print("right")
            front.write(165)
            bw.speed = 50
            bw.backward()
        elif stabilized_steer >= 150:
            #sharp right
            print("hard right")
            front.write(175)
            bw.speed = 50
            bw.backward()
        elif stabilized_steer < 80 and stabilized_steer >= 50:
            #turn left
            print("left")
            front.write(140)
            bw.speed = 50
            bw.backward()
        elif stabilized_steer < 50 and stabilized_steer >= 0:
            #sharp left
            print("hard left")
            front.write(130)
            bw.speed = 50
            bw.backward()
        else:
            #stop
            print("second stop")
            bw.speed = 0
            bw.stop()
            
        
        if cv2.waitKey(1) == ord('q'): #Press Q to quit
            break
        if start:
            bw.speed = 30
            bw.backward()
            start = False
        
    else:
#         continue
        bw.stop()
        time.sleep(3)
        bw.speed = 50
        bw.backward()
        go = True
    
bw.stop()
video.release()
# lidar.stop_motor()
# lidar.stop()
#  
# lidar.disconnect()

atexit.register(killEverything)