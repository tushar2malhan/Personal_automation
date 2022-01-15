import time,datetime
from PIL import ImageGrab
import os


import cv2
import cv2 as cv
import numpy as np
# import matplotlib.pyplot as plt

import pytesseract as tess
import datetime
tess.pytesseract.tesseract_cmd =r'D:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image   #pip install SpeechRecognition


#                             Taking ss and saving it to local
# from PIL import ImageGrab
# save_path=(fr'C:\Users\DELL\Desktop\PYTHON\screenshots_by_bot\snapshot_{datetime.datetime.today().day}.jpg')
# snapshot = ImageGrab.grab()
# snapshot.save(save_path)
# print(all_files_ss)
# os.chdir(r'c:/Users/DELL/Desktop/PYTHON/')

#                              Extracting all the content from the screenshots
# os.chdir(r'C:\Users\DELL\Desktop\ss')
# all_files_ss =os.listdir()
# for i in all_files_ss:
#      img = Image.open(fr'C:\Users\DELL\Desktop\ss\{i}')
#      i = i.split('.jpg')[0]
#      text = tess.image_to_string(img)
#      with open(fr'C:\Users\DELL\Desktop\PYTHON\projects\{i}.txt','w') as f:
#           f.write(text) 




##################################################################################################
#                       coint counter running in venv
##################################################################################################

# path =r"C:\Users\DELL\Desktop\PYTHON\projects\pics_test\coin.jpg"
# path =r""


# image = cv2.imread(path)
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# # plt.imshow(gray, cmap='gray')

# blur = cv2.GaussianBlur(gray, (11,11), 0)
# # plt.imshow(blur, cmap='gray')

# canny = cv2.Canny(blur, 30, 150, 3)
# # plt.imshow(canny, cmap='gray')

# dilated = cv2.dilate(canny, (1,1), iterations = 2)
# # plt.imshow(dilated, cmap='gray')

# (cnt, heirarchy) = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# cv2.drawContours(rgb, cnt, -1, (0,255,0), 2)

# plt.imshow(rgb)


# print('total objects in the image: ', len(cnt))
# plt.show()

##################################################################################################




# face_cascade = cv2.CascadeClassifier(r'C:\Users\DELL\Desktop\PYTHON\opencv\face.xml')
# cap = cv2.VideoCapture(0)

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


################################################################################

####                          take multiple screenshots
# import cv2 , time , os , uuid 

# IMAGES_PATH =r'C:\Users\DELL\Desktop\PYTHON\test\images'

# labels = ['face']
# number_imgs=10


# for label in labels:
#      os.mkdir(r"C:\Users\Tushar\Desktop\python\\"+label)
#      cap = cv2.VideoCapture(0)
#      print('Collecting images for label {}'.format(label))
#      # time.sleep(5)
#      for imgnum in range(number_imgs):
#           ret,frame = cap.read()
#           imagename=os.path.join(IMAGES_PATH ,label,str(imgnum+1)+' '+label+'_image'+'.jpg')
#           cv2.imwrite(imagename,frame)
#           cv2.imshow('frame',frame)
#           time.sleep(2)

#           if cv2.waitKey(1) & 0xFF == ord('q'):
#                break
#      cap.release()
#      cv2.destroyAllWindows()
#######################################################################################################################




