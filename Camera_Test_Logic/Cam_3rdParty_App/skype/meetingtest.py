import os
import pyautogui
import time
from time import sleep

durtn = 30
itr = 3
i = 0
try:
    # open Zoom application
    os.startfile("C:/Users/Test/AppData/Roaming/Zoom/bin/Zoom.exe")
    sleep(2)
    # login Optional
    signin = pyautogui.locateCenterOnScreen("Zsignin.PNG")
    pyautogui.moveTo(signin)
    pyautogui.click()

    time.sleep(2)
    usrnm = pyautogui.locateCenterOnScreen("ZMailAddress.PNG")
    pyautogui.moveTo(usrnm)
    pyautogui.click()
    pyautogui.write('surya-mailid')
    time.sleep(2)
    pwd = pyautogui.locateCenterOnScreen("Zpassword.PNG")
    pyautogui.moveTo(pwd)
    pyautogui.click()
    pyautogui.write('surya-paaaword')
    time.sleep(2)
    sign = pyautogui.locateCenterOnScreen("Z_sign.PNG")
    pyautogui.moveTo(sign)
    pyautogui.click()
    time.sleep(5)
    # settings
    usr = pyautogui.locateCenterOnScreen("zuser.PNG")
    pyautogui.moveTo(usr)
    pyautogui.click()
    time.sleep(2)
    settings = pyautogui.locateCenterOnScreen("zsettings.PNG")
    pyautogui.moveTo(settings)
    pyautogui.click()
    time.sleep(2)
    pyautogui.getWindowsWithTitle('Zoom')[0].close()
    device = pyautogui.locateCenterOnScreen("Zvideo.PNG")
    pyautogui.moveTo(device)
    pyautogui.click()
    time.sleep(2)
    # Select Camera as Jabra Panacast Camera
    pyautogui.moveTo(x=700, y=360)

    pyautogui.click()
    time.sleep(2)
    camera = pyautogui.locateCenterOnScreen("Camllist.PNG")
    pyautogui.moveTo(camera)
    pyautogui.click()
    time.sleep(2)
    setcam = pyautogui.locateCenterOnScreen("ZoomJabraCam.PNG")
    pyautogui.moveTo(setcam)
    pyautogui.click()
    time.sleep(2)
    save = pyautogui.locateCenterOnScreen("zsave.PNG")
    pyautogui.moveTo(save)
    pyautogui.click()
    time.sleep(2)
    os.startfile("C:/Users/Test/AppData/Roaming/Zoom/bin/Zoom.exe")

except Exception as e:
    print(e)
now = time.time()


# Call based on iteration

def zoommeet():
    while True:
        # Start zoom meetings
        # os.startfile("C:/Users/Rahul/AppData/Roaming/Zoom/bin/Zoom.exe")
        DemoMeetOne = pyautogui.locateCenterOnScreen("Zmeetings.PNG")
        pyautogui.moveTo(DemoMeetOne)
        pyautogui.click()
        time.sleep(2)
        join = pyautogui.locateCenterOnScreen("Zstart.PNG")
        pyautogui.moveTo(join)
        pyautogui.click()
        time.sleep(10)
        audiooff = pyautogui.locateCenterOnScreen("Zaudiodevice.PNG")
        pyautogui.moveTo(audiooff)
        pyautogui.click()
        time.sleep(2)
        pyautogui.click()
        mute = pyautogui.locateCenterOnScreen("Zmute.PNG")
        pyautogui.moveTo(mute)
        pyautogui.click()
        time.sleep(durtn)
        newt = time.time()
        diff = newt - now
        if diff > durtn:
            pyautogui.click()
            end = pyautogui.locateCenterOnScreen("Zend.PNG")
            pyautogui.moveTo(end)
            pyautogui.click()
            leave = pyautogui.locateCenterOnScreen("Zendmeeting.PNG")
            pyautogui.moveTo(leave)
            pyautogui.click()
            time.sleep(1)
            break


# iteration for number of Calls
for i in range(0, itr):
    zoommeet()
    i += 1
# Close the App after iteration
time.sleep(2)
pyautogui.click()
closeapp = pyautogui.locateCenterOnScreen("Zcloseapp.PNG")
pyautogui.moveTo(closeapp)
pyautogui.click()
time.sleep(2)
os.system("taskkill /f /im Zoom.exe")