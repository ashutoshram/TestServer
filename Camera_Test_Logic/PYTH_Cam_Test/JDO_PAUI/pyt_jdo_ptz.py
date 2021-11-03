# Author-Rahul Kumar Panda
# @mailid-rkpanda@jbara.com

import pyautogui as jdo, time
import imutils
import cv2
import os
import exception as e


def jdo_izvd_check():
    os.startfile("C:/Program Files (x86)/Jabra/Direct4/jabra-direct.exe")
    time.sleep(10)  # give 10 seconds for JDO to Lunch
    dir = os.getcwd()
    print(dir)
    try:
        device = jdo.locateCenterOnScreen(dir + "/JDO_PAUI/Python_Settings_22.png")
        time.sleep(2)
        jdo.moveTo(device)
        if device:
            jdo.moveTo(device)
            jdo.click()
            time.sleep(5)
        else:
            device = jdo.locateCenterOnScreen(
                dir + "/JDO_PAUI/Python_Settings_11.png")
            jdo.moveTo(device)
            jdo.click()
            time.sleep(5)
    except:
        print(e)
    Cam_control = jdo.locateCenterOnScreen(
        dir + "/JDO_PAUI/Camera_Settings_2.PNG")
    jdo.moveTo(Cam_control)
    jdo.click()
    time.sleep(2)
    jdo.getWindowsWithTitle("Jabra Direct")[0].hide()
    time.sleep(3)

    jdo_izo = jdo.locateCenterOnScreen(
        dir + "/JDO_PAUI/Cam_iz_on.PNG")
    if jdo_izo:
        jdo.moveTo(jdo_izo)
        jdo.click()
        time.sleep(3)
        iz_toggle = jdo.locateCenterOnScreen(dir + "/JDO_PAUI/ptz_iz_toggle.PNG")
        jdo.moveTo(iz_toggle)
        jdo.click()
        # jdo.click(x=1290, y=190)  # x=1300,y=270 For in camera Whiteboard View
        time.sleep(2)
        iz = 'IZ-OFF'

    else:
        iz = 'IZ-OFF'
    jdo_close(dir)
    return iz, dir


def jdo_run(itr, zoom_type):
    os.startfile("C:/Program Files (x86)/Jabra/Direct4/jabra-direct.exe")
    time.sleep(10)  # give 10 seconds for JDO to Lunch
    dir = os.getcwd()
    print(dir)

    device = jdo.locateCenterOnScreen(dir + "/JDO_PAUI/Python_Settings_1.png", confidence=0.8)
    if device:
        jdo.moveTo(device)
        jdo.click()
        time.sleep(5)
    else:
        device = jdo.locateCenterOnScreen(
            dir + "/JDO_PAUI/Python_Settings_12.png")
        jdo.moveTo(device)
        jdo.click()
        time.sleep(5)

    Cam_control = jdo.locateCenterOnScreen(
        dir + "/JDO_PAUI/Camera_Settings_2.PNG")
    jdo.moveTo(Cam_control)
    jdo.click()
    time.sleep(2)
    jdo.getWindowsWithTitle("Jabra Direct")[0].hide()

    time.sleep(5)
    if zoom_type.upper() == 'IN':
        for zi in range(itr):
            Zoom_in = jdo.locateCenterOnScreen(
                dir + "/JDO_PAUI/Zoom_in.PNG")
            jdo.moveTo(Zoom_in)
            jdo.click()
            time.sleep(5)
            # gui.click(1005, 567)
            zi += 1
    # time.sleep(5)
    elif zoom_type.upper() == 'OUT':
        for zo in range(itr):
            Zoom_out = jdo.locateCenterOnScreen(
                dir + "/JDO_PAUI/Zoom_out.PNG")
            jdo.moveTo(Zoom_out)
            jdo.click()
            time.sleep(5)
            # gui.click(1005, 680)
            zo += 1


def make_iz_on(dir):
    jdo_iz = jdo.locateCenterOnScreen(
        dir + "/JDO_PAUI/Cam_iz_off.PNG")
    if jdo_iz:
        jdo.moveTo(jdo_iz)
        jdo.click()
        time.sleep(3)
        iz_toggle = jdo.locateCenterOnScreen(dir + "/JDO_PAUI/ptz_iz_toggle_off.PNG")
        jdo.moveTo(iz_toggle)
        jdo.click()
        print('click iz on')
        #jdo.click(x=1290, y=190)  # x=1300,y=270 For Incamera Whiteboard View
        jdo_close(dir)


def jdo_close(dir):
    print('in jdo close folder')
    time.sleep(3)
    ptz_reset=video_stng_close = jdo.locateCenterOnScreen(
        dir + "/JDO_PAUI/ptz_reset1.PNG")
    jdo.moveTo(ptz_reset)
    jdo.click()
    time.sleep(2)
    video_stng_close = jdo.locateCenterOnScreen(
        dir + "/JDO_PAUI/Jdo_vd_st_close.PNG")
    jdo.moveTo(video_stng_close)
    jdo.click()
    time.sleep(2)
    print('closing the process jdo')
    os.system("taskkill /f /im jabra-direct.exe")
    time.sleep(3)


