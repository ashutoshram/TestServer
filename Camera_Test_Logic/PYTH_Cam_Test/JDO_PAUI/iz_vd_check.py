# Author-Rahul Kumar Panda
# @mailid-rkpanda@jbara.com
import pyautogui as jdo, time
import cv2
import os
import sys

def jdo_run():
    global iz
    if sys.platform == "win32":
        print('host machine is:-',sys.platform)
        os.startfile("C:/Program Files (x86)/Jabra/Direct4/jabra-direct.exe")
        time.sleep(10)  # give 2 seconds for firefox to launch
    elif sys.platform == "darwin":
        os.system('open /Application/"Jabra Direct".app')

    dir = os.getcwd()
    print(dir)
    device = jdo.locateCenterOnScreen(
        dir+"/JDO_PAUI/Python_Settings_1.PNG")
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
        dir+"/JDO_PAUI/Camera_Settings_2.PNG")
    jdo.moveTo(Cam_control)
    jdo.click()
    time.sleep(2)
    jdo.getWindowsWithTitle("Jabra Direct")[0].hide()
    time.sleep(5)
    jdo.moveTo(x=1350, y=65)
    cls_video = jdo.locateCenterOnScreen(dir+'/JDO_PAUI/Close_Video_pyt2.png')
    jdo.moveTo(cls_video)
    jdo.click()
    jdo.sleep(2)

    jdo_iz = jdo.locateCenterOnScreen(
        dir+"/JDO_PAUI/Cam_iz_off.PNG")
    if jdo_iz:
        print('IZ_VD_Off')
        jdo.moveTo(jdo_iz)
        jdo.click()
        time.sleep(2)
        jdo.click(x=1290, y=190)  # x=1300,y=270 For Incamera Whiteboard View
        time.sleep(2)
        iz= 'iz-ON'
        print(iz)
    else:
        jdo_iz2 = jdo.locateCenterOnScreen(
            dir+"/JDO_PAUI/Cam_iz_on.PNG")
        if jdo_iz2:
            iz='iz-ON'
            print(iz)
    video_stng_close = jdo.locateCenterOnScreen(
        dir+"/JDO_PAUI/Close_Cam_Control.png")
    jdo.moveTo(video_stng_close)
    jdo.click()
    time.sleep(2)
    print('closing the process jdo')
    os.system("taskkill /f /im jabra-direct.exe")
    return iz
