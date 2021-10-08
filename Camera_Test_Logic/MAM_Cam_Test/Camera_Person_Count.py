import cv2
import time
import numpy as np
import imutils

# Load the cascade
face_LBP = cv2.CascadeClassifier(cv2.data.lbpcascades + "lbpcascade_frontalface.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
# body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "HS.xml")

# To capture video from webcam.

cap = cv2.VideoCapture(1)

while True:

    ret, img = cap.read()
    img = cv2.resize(img, (1280, 720))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_LBP.detectMultiScale(gray, 1.3, 3)
    # bodies = body_cascade.detectMultiScale(gray, 1.1, 4)
    face_count = 0
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # (x,y) is starting point
        # (x+w,y+h) is the ending point
        # (255,0,0) - > blue rectangle
        # 2 is the alignment

        # eye inside face
        # region of interest
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        eye_count = 0
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            eye_count += 1
            cv2.putText(img, 'eye-' + str(eye_count), (x + 15, y + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if eye_count >= 1:
            face_count += 1
            cv2.putText(img, 'person-' + str(face_count), (x - 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 255), 2)
    # img=imutils.resize(img, width=min(100, img.shape[1]))
    """for (bx, by, bw, bh) in bodies:
        cv2.rectangle(img, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)"""
    cv2.imshow('img', img)
    k = cv2.waitKey(20) & 0xff
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()
