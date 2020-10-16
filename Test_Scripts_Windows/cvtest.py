import cv2
import os
import sys
import time

cam = cv2.VideoCapture(2)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cv2.namedWindow("capture", cv2.WINDOW_NORMAL)
cv2.resizeWindow("capture", (1280, 720))

fps = [30.0, 27.0, 24.0, 15.0, 30.0]
i = 0

while True:
    # retval, frame = cam.read()
    # cv2.imshow("capture", frame)

    # if retval is not True:
    #     break

    # k = cv2.waitKey(1)
    # # ESC pressed
    # if k%256 == 27:
    #     print("Escape hit, closing...")
    #     break
    # # SPACE pressed
    # elif k%256 == 32:
    #     if i >= len(fps):
    #         break
    #     print("Current FPS: {}".format(cam.get(cv2.CAP_PROP_FPS)))
    #     cam.set(cv2.CAP_PROP_FPS, fps[i])
    #     print("FPS set to {}".format(cam.get(cv2.CAP_PROP_FPS)))
    #     i += 1

    if i >= len(fps):
        break
    print("Current FPS: {}".format(cam.get(cv2.CAP_PROP_FPS)))
    print("Setting FPS to: {}".format(fps[i]))
    cam.set(cv2.CAP_PROP_FPS, fps[i])
    time.sleep(3)
    print("FPS set to {}".format(cam.get(cv2.CAP_PROP_FPS)))
    i += 1

cam.release()
cv2.destroyAllWindows()
