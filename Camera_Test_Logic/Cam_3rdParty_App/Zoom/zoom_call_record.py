import os
import pyautogui as zoom_meet
import time
from time import sleep

# import ZoomAPI
durtn = 30
itr = 3
i = 0


# from Camera_Test_Logic.Cam_3rdParty_App.Zoom import ZoomAPI

def zoom_record():
    zoomdct = "C:\\Users\\Rahul\\PycharmProjects\\pythonProject\\Camera_Test_Logic\\Cam_3rdParty_App\\Zoom"
    try:
        # open Zoom application
        # Please Include your file/executable location for zoom application
        os.startfile("C:/Users/Rahul/AppData/Roaming/Zoom/bin/Zoom.exe")
        sleep(2)

        # login Optional
        signin = zoom_meet.locateCenterOnScreen(zoomdct + "\\Zsignin.PNG")
        zoom_meet.moveTo(signin)
        zoom_meet.click()
        # time.sleep(3)
        usrnm = zoom_meet.locateCenterOnScreen(zoomdct + "\\ZMailAddress.PNG")
        zoom_meet.moveTo(usrnm)
        zoom_meet.click()
        zoom_meet.write('prasad.andhugula@altiasystems.com')
        time.sleep(2)
        pwd = zoom_meet.locateCenterOnScreen(zoomdct + "\\Zpassword.PNG")
        zoom_meet.moveTo(pwd)
        zoom_meet.click()
        zoom_meet.write('Test123$')
        time.sleep(2)
        sign = zoom_meet.locateCenterOnScreen(zoomdct + "\\Z_sign.PNG")
        zoom_meet.moveTo(sign)
        zoom_meet.click()
        time.sleep(10)
        # settings
        usr = zoom_meet.locateCenterOnScreen(zoomdct + "\\Z_TestUserP.PNG")
        zoom_meet.moveTo(usr)
        zoom_meet.click()
        time.sleep(2)
        settings = zoom_meet.locateCenterOnScreen(zoomdct + "\\zsettings.PNG")
        zoom_meet.moveTo(settings)
        zoom_meet.click()
        time.sleep(2)
        zoom_meet.getWindowsWithTitle('Zoom')[0].close()
        device = zoom_meet.locateCenterOnScreen(zoomdct + "\\Zvideo.PNG")
        zoom_meet.moveTo(device)
        zoom_meet.click()
        time.sleep(2)
        # Select Camera as Jabra Panacast Camera
        zoom_meet.moveTo(x=700, y=360)

        zoom_meet.click()
        time.sleep(2)
        camera = zoom_meet.locateCenterOnScreen(zoomdct + "\\Camllist.PNG")
        zoom_meet.moveTo(camera)
        zoom_meet.click()
        time.sleep(2)
        setcam = zoom_meet.locateCenterOnScreen(zoomdct + "\\ZoomJabraCam.PNG")
        zoom_meet.moveTo(setcam)
        zoom_meet.click()
        time.sleep(2)
        save = zoom_meet.locateCenterOnScreen(zoomdct + "\\zsave.PNG")
        zoom_meet.moveTo(save)
        zoom_meet.click()
        time.sleep(2)
        os.startfile("C:/Users/Rahul/AppData/Roaming/Zoom/bin/Zoom.exe")
        time.sleep(3)
        DemoMeetin = zoom_meet.locateCenterOnScreen(zoomdct + "\\Z_Meet.PNG")
        zoom_meet.moveTo(DemoMeetin)
        zoom_meet.click()
    except Exception as e:
        print(e)
    now = time.time()

    def recordcall():
        strtrecrd = zoom_meet.locateCenterOnScreen(zoomdct + "\\z_record.PNG")
        zoom_meet.moveTo(strtrecrd)
        zoom_meet.click()
        time.sleep(2)
        return 'record start'

    # Call based on iteration

    def zoommeet():
        global diff
        while True:
            # Start zoom meetings
            # os.startfile("C:/Users/Rahul/AppData/Roaming/Zoom/bin/Zoom.exe")
            DemoMeetOne = zoom_meet.locateCenterOnScreen(zoomdct + "\\Zmeetings.PNG")
            zoom_meet.moveTo(DemoMeetOne)
            zoom_meet.click()
            time.sleep(2)
            join = zoom_meet.locateCenterOnScreen(zoomdct + "\\Zstart.PNG")
            zoom_meet.moveTo(join)
            zoom_meet.click()
            time.sleep(10)
            audiooff = zoom_meet.locateCenterOnScreen(zoomdct + "\\Zaudiodevice.PNG")
            zoom_meet.moveTo(audiooff)
            zoom_meet.click()
            time.sleep(2)
            zoom_meet.click()
            mute = zoom_meet.locateCenterOnScreen(zoomdct + "\\Zmute.PNG")
            zoom_meet.moveTo(mute)
            zoom_meet.click()
            time.sleep(2)
            recd = recordcall()
            if recd == 'record start':
                time.sleep(durtn)
                newt = time.time()
                diff = newt - now
            if diff > durtn:
                zoom_meet.click()
                end = zoom_meet.locateCenterOnScreen(zoomdct + "\\Zend.PNG")
                zoom_meet.moveTo(end)
                zoom_meet.click()
                leave = zoom_meet.locateCenterOnScreen(zoomdct + "\\Zendmeeting.PNG")
                zoom_meet.moveTo(leave)
                zoom_meet.click()
                time.sleep(1)
                break
        return 'Call End'

    from Camera_Test_Logic.Cam_3rdParty_App.Zoom import ZoomAPI
    mid, mpass = ZoomAPI.meetin()
    print(mid)
    print(mpass)
    # iteration for number of Calls
    call = zoommeet()
    if call == 'Call End':
        mtdel = ZoomAPI.deltm()
        homepg=zoom_meet.locateCenterOnScreen(zoomdct + "\\home_button.PNG")
        print(mtdel)
        zoom_meet.moveTo(homepg)
        zoom_meet.click()
        time.sleep(2)
    # Close the App after iteration
    time.sleep(2)
    # zoom_meet.click()
    closeapp = zoom_meet.locateCenterOnScreen(zoomdct + "\\Zcloseapp.PNG")
    zoom_meet.moveTo(closeapp)
    zoom_meet.click()
    time.sleep(2)
    os.system("taskkill /f /im Zoom.exe")
    return mid
