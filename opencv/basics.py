# pip install opencv-contrib-python , caer
import cv2 as cv
import numpy as np

import cv2

# blank = np.zeros((500,500,3) , dtype='uint8')   # resize image
# # cv.imshow('blank image', blank)            # displays img on new window

#     displays img on new window
# img = cv.imread(r'D:\Users\tusha\Desktop\PYTHON\screenshots_by_bot\pd_log.jpg')
# cv.imshow('Image', img)            

#         make image color grey 
# gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# cv.imshow('Gray', gray) 



#         make image BLUR
# blur = cv.GaussianBlur(gray, (7,7), cv.BORDER_DEFAULT)
# cv.imshow('Blur', blur)


#        make image unreadable
# canny = cv.Canny(blur, 125, 175)
# cv.imshow('Canny Edges', canny)                       


# Resize
# resized = cv.resize(img, (1000,1000), interpolation=cv.INTER_CUBIC)
# cv.imshow('Resized', resized)

# Cropping
# cropped = img[50:200, 200:400]
# cv.imshow('Cropped', cropped)

# Flipping
# flip = cv.flip(img, -1)
# cv.imshow('Flip', flip)



#         CHANGES ON BLANK IMAGE 
# blank = np.zeros((500,500,3) , dtype='uint8')   # resize image
# cv.imshow('blank image', blank)    

# contours, hierarchies = cv.findContours(canny, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
# print(f'{len(contours)} contour(s) found!')

# cv.drawContours(blank, contours, -1, (0,0,255), 1)
# cv.imshow('Contours Drawn', blank)


# blank[200:300] = 0,0,255
# cv.imshow('Green', blank)

# cv.rectangle(blank,(0,0),(250,500),(0,250,0) , thickness=2)
# cv.imshow('Rectangle',blank) 

# cv.putText(blank,"Hello " ,(0,225),
#  cv.FONT_HERSHEY_TRIPLEX,1.0 ,(0,255,0),2 )
# cv.imshow('Text',blank)







# Reading Videos
# capture = cv.VideoCapture(r'D:\Users\tusha\Desktop\PYTHON\youtube_downloaded_videosBY_bot\rock.3gpp')
# while True:
#     isTrue, frame = capture.read()         # reads video frame by frame. 
#     if isTrue:    
#         cv.imshow('Video', frame)
#         if cv.waitKey(20) & 0xFF==ord('d'):    #  if press d , come out of window and loop
#             break            
#     else:
#         break

# capture.release()
# cv.destroyAllWindows()


''' face dectectention '''

# # face detenction        IMAGE
# img = cv.imread(r'D:\Users\tusha\Desktop\PYTHON\screenshots_by_bot\group.jpg')
# cv.imshow('Image', img)   

# # needs to convert into gray image first       
# gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)     

# haar_cascade = cv.CascadeClassifier('face.xml')
# faces_rect = haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=1)
# print(f'Number of faces found = {len(faces_rect)}')

# for (x,y,w,h) in faces_rect:
#     cv.rectangle(img, (x,y), (x+w,y+h), (0,255,0), thickness=2)

# cv.imshow('Detected Faces', img)

# cv.waitKey(0)          # wait for specific delay for a key to be processed



'''               face detenction      LIVE  VIDEO   '''
face_cascade = cv.CascadeClassifier(r'C:\Users\DELL\Desktop\PYTHON\opencv\face.xml')
cap = cv2.VideoCapture(0)

# # To use a video file as input 
# # cap = cv2.VideoCapture('filename.mp4')


# while True:
#     # Read the frame
#     _, img = cap.read()

    
# #     # Convert to grayscale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     #     # Detect the faces
#     faces = face_cascade.detectMultiScale(gray, 1.1, 4)

#     # Draw the rectangle around each face
#     for (x, y, w, h) in faces:
#         cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
#       # # Display
#     cv2.imshow('img', img)

#      # ESC to Stop 
#     k = cv2.waitKey(30) & 0xff
#     if k==27:
#         break

# # Release the VideoCapture object
# cap.release()
# cv2.destroyAllWindows()

# import time
# cap = cv2.VideoCapture(0)
# cap.set(3,80)
# cap.set(4,780)

# while True:
#      success,img = cap.read()
#      cTime = time.time()

#      cv2.imshow('img',img)

#      camera.release()
     



