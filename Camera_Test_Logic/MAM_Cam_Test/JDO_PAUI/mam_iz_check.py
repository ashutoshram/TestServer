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
        "jpc_20.PNG")
    jdo.moveTo(device)
    jdo.click()
    time.sleep(5)
    Cam_control = jdo.locateCenterOnScreen(
        "Camera_Settings_2.PNG")
    jdo.moveTo(Cam_control)
    jdo.click()
    time.sleep(2)
    jdo.getWindowsWithTitle("Jabra Direct")[0].hide()
    time.sleep(5)
    jdo.moveTo(x=1350,y=65)
    cls_video=jdo.locateCenterOnScreen('Close_video_mam.png')
    jdo.moveTo(cls_video)
    jdo.click()
    jdo.sleep(2)
    """for zi in range(5):
        Zoom_in = jdo.locateCenterOnScreen(
            "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/Zoom_in.PNG")
        jdo.moveTo(Zoom_in)
        jdo.click()
        time.sleep(5)
        # gui.click(1005, 567)
        zi += 1
    for zo in range(5):
        Zoom_out = jdo.locateCenterOnScreen(
            "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/Zoom_out.PNG")
        jdo.moveTo(Zoom_out)
        jdo.click()
        time.sleep(5)
        # gui.click(1005, 680)
        zo += 1"""

    jdo_iz = jdo.locateCenterOnScreen(
        "Cam_iz_off.PNG")
    if jdo_iz:
        print('IZ_VD_Off')
        jdo.moveTo(jdo_iz)
        jdo.click()
        time.sleep(2)
        jdo.click(x=1300, y=190)  # x=1300,y=270 For Incamera Whiteboard View
        time.sleep(2)
        iz= 'IZ-Made-ON'
        print(iz)
    else:
        jdo_iz2 = jdo.locateCenterOnScreen(
            "Cam_iz_on.PNG")
        if jdo_iz2:
            iz = 'iz-ON'
            print(iz)
    video_stng_close = jdo.locateCenterOnScreen(
        "Close_Cam_Control.png")
    jdo.moveTo(video_stng_close)
    jdo.click()
    time.sleep(2)
    print('closing the process jdo')
    os.system("taskkill /f /im jabra-direct.exe")
    return iz
