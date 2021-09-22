import os
import pyautogui as zoom_meet
import time
from time import sleep
#import ZoomAPI
durtn = 30
itr = 3
i = 0
try:
    # open Zoom application
    os.startfile("C:/Users/Rahul/AppData/Roaming/Zoom/bin/Zoom.exe")
    sleep(2)
    # login Optional
    signin = zoom_meet.locateCenterOnScreen("Zsignin.PNG")
    zoom_meet.moveTo(signin)
    zoom_meet.click()
    #time.sleep(3)
    usrnm = zoom_meet.locateCenterOnScreen("ZMailAddress.PNG")
    zoom_meet.moveTo(usrnm)
    zoom_meet.click()
    zoom_meet.write('prahul3699@gmail.com')
    time.sleep(2)
    pwd = zoom_meet.locateCenterOnScreen("Zpassword.PNG")
    zoom_meet.moveTo(pwd)
    zoom_meet.click()
    zoom_meet.write('R@hul@0438')
    time.sleep(2)
    sign = zoom_meet.locateCenterOnScreen("Z_sign.PNG")
    zoom_meet.moveTo(sign)
    zoom_meet.click()
    time.sleep(10)
    # settings
    usr = zoom_meet.locateCenterOnScreen("zuser.PNG")
    zoom_meet.moveTo(usr)
    zoom_meet.click()
    time.sleep(2)
    settings = zoom_meet.locateCenterOnScreen("zsettings.PNG")
    zoom_meet.moveTo(settings)
    zoom_meet.click()
    time.sleep(2)
    zoom_meet.getWindowsWithTitle('Zoom')[0].close()
    device = zoom_meet.locateCenterOnScreen("Zvideo.PNG")
    zoom_meet.moveTo(device)
    zoom_meet.click()
    time.sleep(2)
    # Select Camera as Jabra Panacast Camera
    zoom_meet.moveTo(x=700, y=360)

    zoom_meet.click()
    time.sleep(2)
    camera = zoom_meet.locateCenterOnScreen("Camllist.PNG")
    zoom_meet.moveTo(camera)
    zoom_meet.click()
    time.sleep(2)
    setcam = zoom_meet.locateCenterOnScreen("ZoomJabraCam.PNG")
    zoom_meet.moveTo(setcam)
    zoom_meet.click()
    time.sleep(2)
    save = zoom_meet.locateCenterOnScreen("zsave.PNG")
    zoom_meet.moveTo(save)
    zoom_meet.click()
    time.sleep(2)
    os.startfile("C:/Users/Rahul/AppData/Roaming/Zoom/bin/Zoom.exe")
    time.sleep(3)
    DemoMeetin = zoom_meet.locateCenterOnScreen("Z_Meet.PNG")
    zoom_meet.moveTo(DemoMeetin)
    zoom_meet.click()
except Exception as e:
    print(e)
now = time.time()


# Call based on iteration

def zoommeet():
    while True:
        # Start zoom meetings
        #os.startfile("C:/Users/Rahul/AppData/Roaming/Zoom/bin/Zoom.exe")
        DemoMeetOne = zoom_meet.locateCenterOnScreen("Zmeetings.PNG")
        zoom_meet.moveTo(DemoMeetOne)
        zoom_meet.click()
        time.sleep(2)
        join = zoom_meet.locateCenterOnScreen("Zstart.PNG")
        zoom_meet.moveTo(join)
        zoom_meet.click()
        time.sleep(10)
        audiooff = zoom_meet.locateCenterOnScreen("Zaudiodevice.PNG")
        zoom_meet.moveTo(audiooff)
        zoom_meet.click()
        time.sleep(2)
        zoom_meet.click()
        mute = zoom_meet.locateCenterOnScreen("Zmute.PNG")
        zoom_meet.moveTo(mute)
        zoom_meet.click()
        time.sleep(durtn)
        newt = time.time()
        diff = newt - now
        if diff > durtn:
            zoom_meet.click()
            end = zoom_meet.locateCenterOnScreen("Zend.PNG")
            zoom_meet.moveTo(end)
            zoom_meet.click()
            leave = zoom_meet.locateCenterOnScreen("Zendmeeting.PNG")
            zoom_meet.moveTo(leave)
            zoom_meet.click()
            time.sleep(1)
            break
import ZoomAPI
mid,mpass= ZoomAPI.meetin()
print(mid)
print(mpass)
# iteration for number of Calls
for i in range(0, itr):
    zoommeet()
    i += 1
mtdel=ZoomAPI.deltm()
print(mtdel)
# Close the App after iteration
time.sleep(2)
#zoom_meet.click()
closeapp = zoom_meet.locateCenterOnScreen("Zcloseapp.PNG")
zoom_meet.moveTo(closeapp)
zoom_meet.click()
time.sleep(2)
os.system("taskkill /f /im Zoom.exe")
#for process in (process for process in psutil.process_iter() if process.name() == "Zoom.exe"):
    #process.kill()
import zjoin_meet
