import cv2
import numpy as np
from matplotlib import pyplot as plt

#Input stopsign data from xml
stop_data = cv2.CascadeClassifier('stop_data.xml')
font = cv2.FONT_HERSHEY_SIMPLEX

#Read in the image
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot access camera")
    exit()
while True:
    #Capture individual frames
    ret, frame = cap.read()

    #ret = true if frame is read correctly
    if not ret: 
        print("Frame can't be loaded, is the camera off?")
        break
    
    #Convert the frame to RGB and display it
    #video = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #Find and label stop signs in the frame
    findSigns = stop_data.detectMultiScale(frame, minSize =(20,20))
    signsFound = len(findSigns)
    if signsFound != 0:
        for (x,y,width,height) in findSigns:
            cv2.rectangle(frame, (x,y), (x + height, y + width), (0,255,0), 5)
            cv2.putText(frame, 'Stop Sign', (x-8,y-15), font, 1, (0,255,0), 4)
    cv2.imshow('Webcam Feed', frame)

    if cv2.waitKey(1) == ord('q'): #Press Q to quit
        break

#Release video camera when ending
cap.release()
cv2.destroyAllWindows()