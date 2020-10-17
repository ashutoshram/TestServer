import cv2
import os
import sys
import time

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cv2.namedWindow("capture", cv2.WINDOW_NORMAL)
cv2.resizeWindow("capture", (1280, 720))

wb = [0, 5000, 6500]
i = 0

while True:
    retval, frame = cam.read()
    cv2.imshow("capture", frame)

    if retval is not True:
        break

    k = cv2.waitKey(1)
    # ESC pressed
    if k%256 == 27:
        print("Escape hit, closing...")
        break
    # SPACE pressed
    elif k%256 == 32:
        if i >= len(wb):
            break
        print("Current white balance: {}".format(cam.get(cv2.CAP_PROP_TEMPERATURE)))
        print("Setting white balance to: {}".format(wb[i]))
        cam.set(cv2.CAP_PROP_TEMPERATURE, wb[i])
        print("wb set to {}".format(cam.get(cv2.CAP_PROP_TEMPERATURE)))
        i += 1

cam.release()
cv2.destroyAllWindows()
