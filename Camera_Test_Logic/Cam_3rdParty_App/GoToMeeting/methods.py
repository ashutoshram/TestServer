import sys
import os
import time
import pyautogui as py

# starting the application
u_name = os.environ.get('USERPROFILE')
# os.environ.get('USERNAME')
# Please add your Local Repo project or code sorce path for Replace with similar to "JabraVideoFW\\TestServer"
# instead of \\PycharmProjects\\pythonProject
g2mdct = u_name + "\\PycharmProjects\\pythonProject\\Camera_Test_Logic\\Cam_3rdParty_App\\GoToMeeting"


def start():
    os.startfile(u_name + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\GoToMeeting.lnk')
    time.sleep(10)


def signin():
    signin1 = py.locateCenterOnScreen(g2mdct + "\\gtm_select.png")
    py.moveTo(signin1)
    py.click()
    time.sleep(3)
    usrnm = py.locateCenterOnScreen(g2mdct + "\\gtm-login-signin1.PNG")
    py.moveTo(usrnm)
    py.click()
    py.write('gnswtest03@jabra.com')
    time.sleep(2)
    usrnm1 = py.locateCenterOnScreen(g2mdct + "\\gtm_login_next1.PNG")
    py.moveTo(usrnm1)
    py.click()
    time.sleep(2)

    signin1 = py.locateCenterOnScreen(g2mdct + "\\gtm_select.png")
    py.moveTo(signin1)
    py.click()
    time.sleep(2)
    pwd1 = py.locateCenterOnScreen(g2mdct + "\\gtm_login_pass2.PNG")
    py.moveTo(pwd1)
    py.click()
    py.write('Jabra123!')
    time.sleep(2)
    sign = py.locateCenterOnScreen(g2mdct + "\\gtm_login_signin1.PNG")
    py.moveTo(sign)
    py.click()
    time.sleep(10)
    ready = py.locateCenterOnScreen(g2mdct + '\\ready1.PNG')
    py.moveTo(ready)
    py.click()
    time.sleep(5)


# starting the call , select meetnow
def meetnow():
    meet = py.locateCenterOnScreen(g2mdct + '\\meet now.PNG')
    py.moveTo(meet)
    py.click()
    time.sleep(8)


# Set the JPC camera as JPC20
def camera():
    jpc20 = py.locateCenterOnScreen(g2mdct + '\\JPC_20.png')
    # jpc = py.locateCenterOnScreen(g2mdct + '\\JPC.png')
    # jpc50 = py.locateCenterOnScreen(g2mdct + '\\JPC_50.png')

    if jpc20:
        py.moveTo(jpc20)
        py.click()
        time.sleep(3)
    else:
        return 'Nocam'
    return 'done'


# for setting the camera
def sett():
    global cam
    sett = py.locateCenterOnScreen(g2mdct + '\\settings.PNG')
    py.moveTo(sett)
    py.click()
    time.sleep(3)
    webcam = py.locateCenterOnScreen(g2mdct + '\\webc.PNG')
    # webcam1 = py.locateCenterOnScreen(g2mdct + '\\JPC_50_1.png')
    # webcam2 = py.locateCenterOnScreen(g2mdct + '\\JPC_1.png')
    closeset = py.locateCenterOnScreen(g2mdct + '\\closeset.PNG')
    closebtn = py.locateCenterOnScreen(g2mdct + '\\clos.PNG')
    dropdown = py.locateCenterOnScreen(g2mdct + '\\dropdown.PNG')

    if webcam:
        time.sleep(2)
        py.moveTo(closeset)
        py.moveTo(closebtn)
        time.sleep(2)
        py.click()
        cam = 'JPC'
    else:
        py.moveTo(dropdown)
        py.click()
        time.sleep(2)
        cam = camera()
    if cam == 'done':
        print('set camera method done')
        py.moveTo(closeset)
        py.moveTo(closebtn)
        py.click()
    else:
        print('Jabra {} camera available'.format(cam))


# changing the Camera View
def view():
    viewtype = py.locateCenterOnScreen(g2mdct + '\\Full_View.PNG')
    py.moveTo(viewtype)
    py.click()
    time.sleep(2)
    everyoneview = py.locateCenterOnScreen(g2mdct + '\\thelayoutview.PNG')
    if everyoneview:
        everyoneview1 = py.locateCenterOnScreen(g2mdct + '\\Activecam.PNG')
        py.moveTo(everyoneview1)
        py.click()
        time.sleep(2)
        max_view = py.locateCenterOnScreen(g2mdct + '\\maximise.PNG')
        py.moveTo(max_view)
        py.click()
        time.sleep(2)
        return "set View"
    else:
        return "No view set"
        pass


# stop recording


# start a recording


# ending the call
def endcall():
    py.click(680, 300)
    leave = py.locateCenterOnScreen(g2mdct + '\\endcall1.PNG')
    py.moveTo(leave)
    py.click()
    time.sleep(2)
    yes = py.locateCenterOnScreen(g2mdct + '\\yesbtn.PNG')
    py.moveTo(yes)
    py.click()
    time.sleep(2)
