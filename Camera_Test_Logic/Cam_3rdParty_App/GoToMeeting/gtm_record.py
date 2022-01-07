# importing the required packages
import pyautogui
import cv2
import numpy as np
import os
import time
# starting the application
u_name = os.environ.get('USERPROFILE')
# os.environ.get('USERNAME')
# Please add your Local Repo project or code sorce path for Replace with similar to "JabraVideoFW\\TestServer"
# intead of \\PycharmProjects\\pythonProject
g2mdct = u_name + "\\PycharmProjects\\pythonProject\\Camera_Test_Logic\\Cam_3rdParty_App\\GoToMeeting"


def record():
    # display screen resolution, get it using pyautogui itself
    SCREEN_SIZE = tuple(pyautogui.size())
    print(SCREEN_SIZE)
    # define the codec
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # frames per second
    fps = 30.0
    # create the video write object
    out = cv2.VideoWriter(g2mdct+'\\'+"output.avi", fourcc, fps, SCREEN_SIZE)
    # the time you want to record in seconds
    record_seconds = 20

    for i in range(int(record_seconds * fps)):
        # make a screenshot
        img = pyautogui.screenshot()
        # convert these pixels to a proper numpy array to work with OpenCV
        frame = np.array(img)
        # convert colors from BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # write the frame
        out.write(frame)
        # show the frame
        # cv2.imshow("g2mrec", frame)
        # if the user clicks q, it exits
        if cv2.waitKey(20) == ord("q"):
            break

    # make sure everything is closed when exited
    cv2.destroyAllWindows()
    out.release()
    time.sleep(2)
    pyautogui.click()
    return 'Record'
