import os
import pyautogui as zoom_meet
import time
import sys

if sys.platform == "win32":
    print('host machine is:-', sys.platform)
    os.startfile("C:/Users/Rahul/AppData/Roaming/Zoom/bin/Zoom.exe")
    time.sleep(5)  # give 2 seconds for firefox to launch
elif sys.platform == "darwin":
    os.system('open /Application/"zoom.us".app')
id = '725 5072 6513'
pas = '46vcsC'
durtn = 30


def join_meet(id, pas):
    joinmeet = zoom_meet.locateCenterOnScreen('Z_join_meet.png')
    zoom_meet.moveTo(joinmeet)
    zoom_meet.click()
    zoom_meet.sleep(2)
    joinmeetid = zoom_meet.locateCenterOnScreen('Z_meet_id1.png')
    zoom_meet.moveTo(joinmeetid)
    zoom_meet.click()
    zoom_meet.write(id)
    zoom_meet.sleep(2)
    joinmeetjn = zoom_meet.locateCenterOnScreen('Z_join_meet1.png')
    zoom_meet.moveTo(joinmeetjn)
    zoom_meet.click()
    zoom_meet.sleep(4)
    joinmeetpw = zoom_meet.locateCenterOnScreen('Z_meet_pass.png')
    zoom_meet.moveTo(joinmeetpw)
    zoom_meet.click()
    zoom_meet.write(pas)
    zoom_meet.sleep(2)
    joinmeetjm = zoom_meet.locateCenterOnScreen('Z_join_meet2.png')
    zoom_meet.moveTo(joinmeetjm)
    zoom_meet.click()
    zoom_meet.sleep(2)
    joinmeetjmv = zoom_meet.locateCenterOnScreen('Z_join_meetv3.png')
    zoom_meet.moveTo(joinmeetjmv)
    zoom_meet.click()
    zoom_meet.sleep(8)
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
        zoom_meet.sleep(1)
        end = zoom_meet.locateCenterOnScreen("Zmleave.PNG")
        zoom_meet.moveTo(end)
        zoom_meet.click()
        zoom_meet.sleep(1)
        leave = zoom_meet.locateCenterOnScreen("Zlmeet1.PNG")
        zoom_meet.moveTo(leave)
        zoom_meet.click()
        time.sleep(1)
    return 'call complete'


now = time.time()
testmeet = join_meet(id, pas)
print(testmeet)
closeapp = zoom_meet.locateCenterOnScreen("Zcloseapp.PNG")
zoom_meet.moveTo(closeapp)
zoom_meet.click()
time.sleep(2)
# os.system("taskkill /f /im Zoom.exe")
