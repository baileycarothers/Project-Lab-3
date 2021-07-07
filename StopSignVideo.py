import cv2

#Input stop sign data from xml
stop_data = cv2.CascadeClassifier('stop_data.xml')
font = cv2.FONT_HERSHEY_SIMPLEX

#Read in the image
cap = cv2.VideoCapture(1)
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
    
    #Convert the frame to gray for sign detection
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #Find and label stop signs in the frame
    findSigns = stop_data.detectMultiScale(frame_gray, minSize =(20,20))
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