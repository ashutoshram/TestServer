import time
import unittest2
from Camera_Test_Logic.MAM_Cam_Test.JDO_PAUI import jdo_pip
from Camera_Test_Logic.MAM_Cam_Test.pip_thrdparty_app import main
from Camera_Test_Logic.Cam_3rdParty_App.Zoom import zoom_call_record
from Camera_Test_Logic.Cam_3rdParty_App.Teams_Meet_Now import meetnow

global app_call


class Test_Mam_cam(unittest2.TestCase):

    def test_pip_on(self):
        global app_call
        pip = "ON"
        thrd_app = 'teams'
        u_fps = 30
        pip_s = jdo_pip.jdo_run(pip)
        print(pip_s)
        time.sleep(3)
        if pip_s.upper() == "PIP-ON" and thrd_app.lower() == "zoom":
            app_call = zoom_call_record.zoom_record()
        elif pip_s.upper() == "PIP-ON" and thrd_app.lower() == "teams":
            app_call = meetnow.tms_meet_now()

            time.sleep(4)
            print(app_call)
            ver_pip = main(thrd_app)
            print(ver_pip)
            self.assertEqual(pip_s.upper(), 'PIP-' + ver_pip)

    def test_pip_off(self):
        global app_call
        pip = "OFF"
        thrd_app = 'teams'
        u_fps = 30
        pip_s = jdo_pip.jdo_run(pip)
        print(pip_s)
        time.sleep(3)
        if pip_s.upper() == "PIP-OFF" and thrd_app.lower() == "zoom":
            app_call = zoom_call_record.zoom_record()
        elif pip_s.upper() == "PIP-OFF" and thrd_app.lower() == "teams":
            app_call = meetnow.tms_meet_now()

        time.sleep(4)
        print(app_call)
        ver_pip = main(thrd_app)
        print(ver_pip)
        self.assertEqual(pip_s.upper(), 'PIP-' + ver_pip)


if __name__ == '__main__':
    unittest2.main()
