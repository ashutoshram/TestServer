"""from PIL import ImageGrab
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)"""
import pyautogui as jdo, time
import imutils
import cv2
import threading
import os
import queue


# initialize the background subtractor
# fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()


def jdo_run():
    os.startfile("C:/Program Files (x86)/Jabra/Direct4/jabra-direct.exe")
    time.sleep(10)  # give 2 seconds for firefox to launch
    dir=os.getcwd()
    print(dir)
    device = jdo.locateCenterOnScreen(
        "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/PYTH_Cam_Test/JDO_PAUI/Python_Settings_1.PNG")
    jdo.moveTo(device)
    jdo.click()
    time.sleep(5)
    Cam_control = jdo.locateCenterOnScreen(
        "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/PYTH_Cam_Test/JDO_PAUI/Camera_Settings_2.PNG")
    jdo.moveTo(Cam_control)
    jdo.click()
    time.sleep(2)
    jdo.getWindowsWithTitle("Jabra Direct")[0].hide()
    for zi in range(5):
        Zoom_in = jdo.locateCenterOnScreen(
            "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/PYTH_Cam_Test/JDO_PAUI/Zoom_in.PNG")
        jdo.moveTo(Zoom_in)
        jdo.click()
        time.sleep(5)
        # gui.click(1005, 567)
        zi += 1
    for zo in range(5):
        Zoom_out = jdo.locateCenterOnScreen(
            "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/PYTH_Cam_Test/JDO_PAUI/Zoom_out.PNG")
        jdo.moveTo(Zoom_out)
        jdo.click()
        time.sleep(5)
        # gui.click(1005, 680)
        zo += 1
    jdo_iz = jdo.locateCenterOnScreen(
        "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/PYTH_Cam_Test/JDO_PAUI/Cam_iz_off.PNG")
    if jdo_iz:
        jdo.moveTo(jdo_iz)
        jdo.click()
        time.sleep(2)
        jdo.click(x=1290,y=190)#x=1300,y=270 For Incamera Whiteboard View
        time.sleep(2)
    video_stng_close = jdo.locateCenterOnScreen(
        "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/PYTH_Cam_Test/JDO_PAUI/Jdo_vd_st_close.PNG")
    jdo.moveTo(video_stng_close)
    jdo.click()
    time.sleep(2)
    print('closing the process jdo')
    os.system("taskkill /f /im jabra-direct.exe")


# vs = cv2.VideoCapture(1)


def maint(vs, queres):
    min_percent = 1.0
    max_percent = 10.0
    warmup = 200
    # initialize the background subtract
    # fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    fgbg = cv2.createBackgroundSubtractorMOG2()

    """initialize a boolean used to represent whether or not a given frame
    has been captured along with two integer counters -- one to count
    the total number of frames that have been captured and another to
    count the total number of frames processed"""
    captured = False
    total = 0
    frames = 0
    """open a pointer to the video file initialize the width and height of
    the frame"""
    start_time = time.time()
    duration = 90
    # vs = cv2.VideoCapture(1)
    (W, H) = (None, None)
    # loop over the frames of the video

    while True:

        # grab a frame from the video
        (grabbed, frame) = vs.read()
        # if the frame is None, then we have reached the end of the video file
        if grabbed is None:
            break
        # resize the frame, and then apply the background subtractor

        frame = imutils.resize(frame, width=720)
        mask = fgbg.apply(frame)
        # apply a series of erosion and dilutions to eliminate noise
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        # if the width and height are empty, grab the spatial dimensions
        if W is None or H is None:
            (H, W) = mask.shape[:2]
        # compute the percentage of the mask that is "foreground"
        p = (cv2.countNonZero(mask) / float(W * H)) * 100
        """if there is less than N% of the frame as "foreground" then we
        know that the motion has stopped and thus we should grab the
        frame"""

        if p < min_percent and not captured and frames > warmup:
            captured = True
            c = 0
            total += 1
            if total >= 1:
                print("[INFO] switching")
                c = total - 1
                text = "PTZ- View"
                col = (100, 255, 0)
                cv2.putText(frame, text + "-" + str(c), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, col, 2)
                cv2.imshow("Captured", frame)
            # save the  *original, high resolution* frame to disk

            print(total)
        # building the background model
        elif captured and p > max_percent:
            captured = False

        txt = "Default View"
        color = (0, 255, 0)
        # display the frame and detect if there is a key press
        cv2.putText(frame, txt, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)
        current_time = time.time()
        elapsed_time = current_time - start_time

        key = cv2.waitKey(1) & 0xFF
        # increment the frames counter
        frames += 1
        # if elapse time reached duration set or the `q` key was pressed, break from the loop
        if elapsed_time > duration or key == ord("q"):
            break
    # destroy opencv window on exit
    cv2.destroyAllWindows()
    queres.put(total)
    return total


def jpc_ptz():
    vs = cv2.VideoCapture(1)
    que = queue.Queue()
    t1 = threading.Thread(target=maint, args=(vs, que))
    t2 = threading.Thread(target=jdo_run, args=())

    # starting thread 1
    t1.start()

    # let fist process start 5 sec pause
    time.sleep(3)
    # starting thread 2
    t2.start()

    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()
    result = que.get()
    print('Result', result)
    # both threads completely executed
    print("Done!")
    return result


if __name__ == '__main__':
    ptz = jpc_ptz()
    print('ptz value:-', ptz)
