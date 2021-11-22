import os
import pyautogui
import time
from time import sleep

durtn = 30
itr = 3
i = 0

os.startfile("C:/Program Files (x86)/Microsoft/Skype for Desktop/skype.exe")
#pyautogui.click()
time.sleep(10)
"""threedots = pyautogui.locateCenterOnScreen("settings1.PNG")
pyautogui.moveTo(threedots)
pyautogui.click()
time.sleep(2)
Settings = pyautogui.locateCenterOnScreen("Ssettings.PNG")
pyautogui.moveTo(Settings)
pyautogui.click()
time.sleep(2)
#pyautogui.getWindowsWithTitle('Skype')[0].close()
device = pyautogui.locateCenterOnScreen("SVideo.PNG")
pyautogui.moveTo(device)
pyautogui.click()
time.sleep(2)
# Select Camera as Jabra Panacast Camera
pyautogui.moveTo(x=950, y=200)
#pyautogui.click()
time.sleep(2)
camera = pyautogui.locateCenterOnScreen("Camllist.PNG")
pyautogui.moveTo(camera)
pyautogui.click()
time.sleep(2)
setcam = pyautogui.locateCenterOnScreen("Spanacast.PNG")
pyautogui.moveTo(setcam)
pyautogui.click()
time.sleep(2)
pyautogui.getWindowsWithTitle('Skype')[0].close()
time.sleep(3)"""
search = pyautogui.locateCenterOnScreen("Ssearchppl.PNG")
pyautogui.moveTo(search)
pyautogui.click()
time.sleep(2)
pyautogui.write("Surya")
time.sleep(3)
people = pyautogui.locateCenterOnScreen("SuryaSearch1.PNG")
pyautogui.moveTo(people)
pyautogui.click()
time.sleep(2)
close = pyautogui.locateCenterOnScreen("CloseSearch.PNG")
pyautogui.moveTo(close)
pyautogui.click()
online = pyautogui.locateCenterOnScreen("SuryaOnline2.PNG")
pyautogui.moveTo(online)
pyautogui.click()
#snd = pyautogui.locateCenterOnScreen("Ssend.PNG")
if online:

    print('entering if block')
    call = pyautogui.locateCenterOnScreen("Scall.PNG")
    pyautogui.moveTo(call)
    time.sleep(2)
    pyautogui.click()
else:
    print('entering else block block')
    msg = pyautogui.locateCenterOnScreen("MessageBox.PNG")
    time.sleep(2)
    pyautogui.moveTo(msg)
    time.sleep(2)
    pyautogui.click()
    time.sleep(2)
    pyautogui.write("Hello, are u there?")
    time.sleep(2)
    snd = pyautogui.locateCenterOnScreen("Ssend.PNG")
    pyautogui.moveTo(snd)
    pyautogui.click()
    time.sleep(2)
    os.system("taskkill /f /im skype.exe")


