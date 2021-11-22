import pyautogui as jdo, time
import cv2
import os
import sys

def viv_on_off(viv_stats):
    print(viv_stats)
    if viv_stats == 'ON':
        jdo_vivof=jdo.locateCenterOnScreen(
            "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/Vividoff.png")
        jdo.moveTo(jdo_vivof)
        time.sleep(2)
        jdo.click()
        time.sleep(4)
        return 'vivid-on'
    elif viv_stats == "OFF":
        jdo_vivon = jdo.locateCenterOnScreen(
            'C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/Vividon.png')
        jdo.moveTo(jdo_vivon)
        time.sleep(2)
        jdo.click()
        time.sleep(4)
        return 'vivid-off'
def is_on_off():
    jdo_vivdof = jdo.locateCenterOnScreen(
        "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/Vivid2.PNG")
    if jdo_vivdof:
        vivid = "OFF"
        print(vivid)
        return vivid
    else:
        jdo_vivdon = jdo.locateCenterOnScreen(
            "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/Vivid1.PNG")
        if jdo_vivdon:
            vivid = "ON"
            print(vivid)
            return vivid
def jdo_run(stat):
    global vivid
    if sys.platform == "win32":
        print('host machine is:-',sys.platform)
        os.startfile("C:/Program Files (x86)/Jabra/Direct4/jabra-direct.exe")
        time.sleep(15)  # give 2 seconds jdo to launch
    elif sys.platform == "darwin":
        os.system('open /Application/"Jabra Direct".app')
        time.sleep(10)
    dir = os.getcwd()
    print(dir)
    device = jdo.locateCenterOnScreen(
        "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/jpc_20.PNG")
    jdo.moveTo(device)
    jdo.click()
    time.sleep(5)
    Cam_control = jdo.locateCenterOnScreen(
        "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/Camera_Settings_2.PNG")
    jdo.moveTo(Cam_control)
    jdo.click()
    time.sleep(3)
    jdo.getWindowsWithTitle("Jabra Direct")[0].hide()
    time.sleep(3)
    jdo.moveTo(x=1350,y=65)
    cls_video=jdo.locateCenterOnScreen('C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/Close_video_mam.png')
    jdo.moveTo(cls_video)
    jdo.click()
    jdo.sleep(2)
    jdo_img_qual=jdo.locateCenterOnScreen(
        "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/ImageQuality1.PNG")
    jdo.click(jdo_img_qual)
    time.sleep(2)
    jdo.scroll(-180)
    time.sleep(2)
    is_vivid=is_on_off()
    if is_vivid != stat:
        vivid = viv_on_off(stat)
    else:
        vivid="vivid-"+is_vivid.lower()
    video_stng_close = jdo.locateCenterOnScreen(
        "C:/Users/Rahul/PycharmProjects/pythonProject/Camera_Test_logic/MAM_Cam_Test/JDO_PAUI/Close_Cam_Control.png")
    jdo.moveTo(video_stng_close)
    jdo.click()
    time.sleep(2)
    print('closing the process jdo')
    os.system("taskkill /f /im jabra-direct.exe")
    return vivid


"""vivdst=jdo_run('ON')
print(vivdst)"""