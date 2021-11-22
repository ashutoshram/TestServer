import os
import pyautogui 
import time
from time import sleep

durtn = 30
itr = 3
i = 0
try:
    # open remote machine connection

    os.startfile("C:/Program Files/PuTTY/putty.exe")
    time.sleep(2)
    tvnhostl = pyautogui.locateCenterOnScreen("tvnhost.PNG")
    pyautogui.moveTo(tvnhostl)
    pyautogui.click()
    time.sleep(2)
    hostnm = pyautogui.locateCenterOnScreen("testmachostnm.PNG")
    pyautogui.moveTo(hostnm)
    pyautogui.click()
    time.sleep(2)
    tvnconnect = pyautogui.locateCenterOnScreen("tvnconct.PNG")
    pyautogui.moveTo(tvnconnect)
    pyautogui.click()
    time.sleep(2)
    tvnpass = pyautogui.locateCenterOnScreen("Tvnpass.PNG")
    pyautogui.moveTo(tvnpass)
    pyautogui.click()
    pyautogui.write('test123$')
    time.sleep(2)
    pyautogui.press('enter')
    # connecting to the remote Mac
    time.sleep(10)
    macin = pyautogui.locateCenterOnScreen("applepassword.PNG")
    pyautogui.moveTo(macin)
    pyautogui.click()
    pyautogui.write('Test123$&')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(5)
    # open MS Teams application
    os.startfile("C:/Users/Rahul/AppData/Local/Microsoft/Teams/current/Teams.exe")
    time.sleep(2)
    # settings
    usr = pyautogui.locateCenterOnScreen("User.PNG")
    pyautogui.moveTo(usr)
    pyautogui.click()
    time.sleep(2)
    settings = pyautogui.locateCenterOnScreen("setng.PNG")
    pyautogui.moveTo(settings)
    pyautogui.click()
    time.sleep(2)
    device = pyautogui.locateCenterOnScreen("devices.PNG")
    pyautogui.moveTo(device)
    pyautogui.click()
    time.sleep(2)
    pyautogui.moveTo(x=1010, y=94)
    time.sleep(2)
    pyautogui.scroll(-200)
    time.sleep(2)
    camera = pyautogui.locateCenterOnScreen("jabra.PNG")
    pyautogui.moveTo(camera)
    pyautogui.click()
    time.sleep(2)
    setcam = pyautogui.locateCenterOnScreen("Cam.PNG")
    pyautogui.moveTo(setcam)
    pyautogui.click()
    time.sleep(2)
    save = pyautogui.locateCenterOnScreen("close.PNG")
    pyautogui.moveTo(save)
    pyautogui.click()
    time.sleep(2)
except Exception as e:
    print(e)
now = time.time()


# Call based on iteration

def teams():
    while True:
        # DemoMeetOne

        DemoMeetOne = pyautogui.locateCenterOnScreen("chart.PNG")
        pyautogui.moveTo(DemoMeetOne)
        pyautogui.click()
        time.sleep(2)
        join = pyautogui.locateCenterOnScreen("extvid.PNG")
        pyautogui.moveTo(join)
        pyautogui.click()
        time.sleep(5)
        audiooff = pyautogui.locateCenterOnScreen("Mute.PNG")
        pyautogui.moveTo(audiooff)
        pyautogui.click()
        time.sleep(2)
        pyautogui.getWindowsWithTitle("Testmac - TightVNC Viewer")[0].activate()
        time.sleep(durtn)
        pyautogui.getWindowsWithTitle("Testmac - TightVNC Viewer")[0].hide()
        newt = time.time()
        diff = newt - now
        if diff > durtn:
            leave = pyautogui.locateCenterOnScreen("leave.PNG")
            pyautogui.moveTo(leave)
            pyautogui.click()
            break


for i in range(0, itr):
    teams()

    i += 1
# Close the App after Operation
time.sleep(2)
pyautogui.click()
closeapp = pyautogui.locateCenterOnScreen("TClose.PNG")
pyautogui.moveTo(closeapp)
pyautogui.click()
pyautogui.getWindowsWithTitle("Testmac - TightVNC Viewer")[0].close()
