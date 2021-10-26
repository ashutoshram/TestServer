import pyautogui as jdo, time
import cv2
import os
import sys


def pip_on_off(pip_stats, dict):
    print(pip_stats)
    jdo.scroll(-120)
    time.sleep(2)
    if pip_stats == 'ON':
        jdo_pipof = jdo.locateCenterOnScreen(
            dict + "\pip_tog_off.png")
        jdo.moveTo(jdo_pipof)
        time.sleep(2)
        jdo.click()
        time.sleep(4)
        return 'pip-on'
    elif pip_stats == "OFF":
        jdo_pipon = jdo.locateCenterOnScreen(
            dict + "\pip_tog_on.png")
        jdo.moveTo(jdo_pipon)
        time.sleep(2)
        jdo.click()
        time.sleep(4)
        return 'pip-off'


def is_on_off(dict):
    time.sleep(2)
    jdo_pipoff = jdo.locateCenterOnScreen(
        dict + "\cam_pip_off.png")
    if jdo_pipoff:
        pipis = "OFF"
        print(pipis)
        return pipis
    else:
        jdo_pipon = jdo.locateCenterOnScreen(
            dict + "\Cam_pip_on.png")
        if jdo_pipon:
            pipis = "ON"
            print(pipis)
            return pipis


def jdo_run(stat):
    global pipval
    if sys.platform == "win32":
        print('host machine is:-', sys.platform)
        os.startfile("C:/Program Files (x86)/Jabra/Direct4/jabra-direct.exe")
        time.sleep(15)  # give 2 seconds jdo to launch
    elif sys.platform == "darwin":
        os.system('open /Application/"Jabra Direct".app')
        time.sleep(10)
    #dict=os.getcwd()
    dict="C:\\Users\\Rahul\\PycharmProjects\\pythonProject\\Camera_Test_Logic\\MAM_Cam_Test\\JDO_PAUI"
    device = jdo.locateCenterOnScreen(
        dict+"\jpc_20.PNG")
    jdo.moveTo(device)
    jdo.click()
    time.sleep(5)
    Cam_control = jdo.locateCenterOnScreen(
         dict+"\Camera_Settings_2.PNG")
    jdo.moveTo(Cam_control)
    jdo.click()
    time.sleep(3)
    jdo.getWindowsWithTitle("Jabra Direct")[0].hide()
    time.sleep(3)

    is_pip = is_on_off(dict)
    time.sleep(3)
    if is_pip != stat:
        pipval = pip_on_off(stat, dict)
    else:
        pipval = "PIP-" + is_pip.lower()
    time.sleep(3)
    jdo.moveTo(x=1350, y=65)
    cls_video = jdo.locateCenterOnScreen(dict + "\Close_video_mam.png")
    jdo.moveTo(cls_video)
    jdo.click()
    jdo.sleep(2)
    video_stng_close = jdo.locateCenterOnScreen(
        dict + "\Close_Cam_Control.png")
    jdo.moveTo(video_stng_close)
    jdo.click()
    time.sleep(2)
    print('closing the process jdo')
    os.system("taskkill /f /im jabra-direct.exe")
    return pipval

#st=jdo_run('ON')
#print(st)
