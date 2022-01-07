import os
import sys
import pyautogui as jdo
import time

global pipval


def pip_on_off(pip_stats, dict_jdo):
    print(pip_stats)
    jdo.scroll(-120)
    time.sleep(2)
    if pip_stats == 'ON':
        jdo_pipof = jdo.locateCenterOnScreen(
            dict_jdo + "\\pip_tog_off.png")
        jdo.moveTo(jdo_pipof)
        time.sleep(2)
        jdo.click()
        time.sleep(4)
        return 'pip-on'
    elif pip_stats == "OFF":
        jdo_pipon = jdo.locateCenterOnScreen(
            dict_jdo + "\\pip_tog_on.png")
        jdo.moveTo(jdo_pipon)
        time.sleep(2)
        jdo.click()
        time.sleep(4)
        return 'pip-off'


def is_on_off(dict_jdo):
    time.sleep(2)
    jdo_pipoff = jdo.locateCenterOnScreen(
        dict_jdo + "\\cam_pip_off.png")
    if jdo_pipoff:
        pipis = "OFF"
        print(pipis)
        return pipis
    else:
        jdo_pipon = jdo.locateCenterOnScreen(
            dict_jdo + "\\Cam_pip_on.png")
        if jdo_pipon:
            pipis = "ON"
            print(pipis)
            return pipis


def jdo_run(stat):
    global pipval
    if sys.platform == "win32":
        print('host machine is:-', sys.platform)
        os.startfile("C:/Program Files (x86)/Jabra/Direct4/jabra-direct.exe")
        time.sleep(20)  # give 20 seconds jdo to launch
    elif sys.platform == "darwin":
        os.system('open /Application/"Jabra Direct".app')
        time.sleep(10)
    # dict=os.getcwd()
    # Please add your Local Repo project or code sorce path for Replace with similar to "JabraVideoFW\\TestServer"
    # intead of \\PycharmProjects\\pythonProject
    dict_jdo = "C:\\Users\\Rahul\\PycharmProjects\\pythonProject\\Camera_Test_Logic\\MAM_Cam_Test\\JDO_PAUI"
    device = jdo.locateCenterOnScreen(
        dict_jdo + "\\jpc_20.PNG")
    jdo.moveTo(device)
    jdo.click()
    time.sleep(5)
    Cam_control = jdo.locateCenterOnScreen(
        dict_jdo + "\\Camera_Settings_2.PNG")
    jdo.moveTo(Cam_control)
    jdo.click()
    time.sleep(3)
    jdo.getWindowsWithTitle("Jabra Direct")[0].hide()
    time.sleep(3)

    is_pip = is_on_off(dict_jdo)
    time.sleep(3)
    if is_pip != stat:
        pipval = pip_on_off(stat, dict_jdo)
    else:
        pipval = "pip-" + is_pip.lower()
    time.sleep(3)
    jdo.moveTo(x=1350, y=65)
    cls_video = jdo.locateCenterOnScreen(dict_jdo + "\\Close_video_mam.png")
    jdo.moveTo(cls_video)
    jdo.click()
    jdo.sleep(2)
    video_stng_close = jdo.locateCenterOnScreen(
        dict_jdo + "\\Close_Cam_Control.png")
    jdo.moveTo(video_stng_close)
    jdo.click()
    time.sleep(2)
    print('closing the process jdo')
    os.system("taskkill /f /im jabra-direct.exe")
    return pipval


