import sys
import os
import time
from Camera_Test_Logic.Cam_3rdParty_App.GoToMeeting import methods
from Camera_Test_Logic.Cam_3rdParty_App.GoToMeeting import gtm_record
from Camera_Test_Logic.Cam_3rdParty_App.GoToMeeting import testvid


def g2mrecord():
    global stat, rec
    if sys.platform == "win32":
        print('host machine is:-', sys.platform)
        os.startfile("C:/Users/Rahul/AppData/Local/GoToMeeting/19932/g2mstart.exe")
        time.sleep(5)
    elif sys.platform == "darwin":
        os.system('open /Application/"g2mstart.dmg".app')

    methods.start()
    time.sleep(1)
    methods.meetnow()
    time.sleep(1)
    methods.signin()
    time.sleep(1)
    methods.sett()
    time.sleep(2)
    views = methods.view()
    if views == "set View":
        rec = gtm_record.record()
    print(rec)
    time.sleep(2)
    if rec == "Record":
        stat = testvid.orig_video()
    if stat == 'Recoded':
        print(stat)

    else:
        print('Not Recoded')
        return 'Not Recoded'

    methods.endcall()
    os.system("taskkill /f /im g2m*")
    return stat
# g2mcomm
# g2mlauncher
# g2mstart
