import cv2
import time
import pyautogui
import os

# starting the application
u_name = os.environ.get('USERPROFILE')
# os.environ.get('USERNAME')
# Please add your Local Repo project or code sorce path for Replace with similar to "JabraVideoFW\\TestServer"
# instead of \\PycharmProjects\\pythonProject
g2mdct = u_name + "\\PycharmProjects\\pythonProject\\Camera_Test_Logic\\Cam_3rdParty_App\\GoToMeeting"


def orig_video():
    gtm_vid = cv2.VideoCapture(g2mdct + '\\' + "output.avi")
    str_time = time.time()
    duration = 20
    gtm_vid.set(5, 15)
    # Take screenshot using PyAutoGUI
    global cropped
    # Convert the screenshot to a numpy array
    roi = (173, 80, 1018, 570)
    # roi = (173, 80, 1016, 572)
    # while True:
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # frames per second
    fps = 15.0
    cnt = 0
    # create the video write object
    out = cv2.VideoWriter(g2mdct + '\\' + "result.avi", fourcc, fps, (1018, 570))
    # Convert the screenshot to a numpy array

    while True:
        rt, frames = gtm_vid.read()
        cnt += 1
        if rt:
            cropped = frames[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]
            # Optional: Display the recording screen

            out.write(cropped)
            cv2.imshow('g2mrecvid', cropped)
            key = cv2.waitKey(1) & 0xFF
            end_time = time.time()
            # Stop recording when we press 'q'
            if key == ord('q') or end_time - str_time >= duration:
                break
        else:
            break

    # Destroy all windows
    gtm_vid.release()
    out.release()
    cv2.destroyAllWindows()
    # pyautogui.click(1016, 572)
    return 'Recoded'
