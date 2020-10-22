import cv2
import cv
import os
import sys
import time

# set up camera stream
# for k in range(4):
#     cam = cv2.VideoCapture(k)
#     if cam.isOpened():
#         print("Panacast device found")
#         break

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cv2.namedWindow("capture", cv2.WINDOW_NORMAL)
cv2.resizeWindow("capture", (1280, 720))

input = [0, 110, 128, 255, 193]
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
        if i >= len(input):
            break

        initial = cam.get(cv2.CAP_PROP_SHARPNESS)
        print("Current sharpness: {}".format(initial))
        print("Setting sharpness to: {}".format(input[i]))
        cam.set(cv2.CAP_PROP_SHARPNESS, input[i])
        final = cam.get(cv2.CAP_PROP_SHARPNESS)
        print("sharpness set to {}".format(final))
        i += 1

cam.release()
cv2.destroyAllWindows()
