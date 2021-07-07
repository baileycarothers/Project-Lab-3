import cv2
import numpy as np
from matplotlib import pyplot as plt

font = cv2.FONT_HERSHEY_SIMPLEX

#Read in the image
img = cv2.imread("fakeStop2.png")

#Above reads as BGR
#now we convert to rgb and grayscale
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#Input stopsign data from xml
stop_data = cv2.CascadeClassifier('stop_data.xml')

findSigns = stop_data.detectMultiScale(img_gray, minSize =(20,20))

signsFound = len(findSigns)

if signsFound != 0:
    for (x,y,width,height) in findSigns:
        cv2.rectangle(img_rgb, (x,y), (x + height, y + width), (0,255,0), 5)
        cv2.putText(img_rgb, 'Stop Sign', (x-8,y-15), font, 1, (0,255,0), 4)

plt.subplot(1,1,1)
plt.imshow(img_rgb)
plt.show()