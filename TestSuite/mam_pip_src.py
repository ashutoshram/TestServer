import time
import unittest2
from Camera_Test_Logic.MAM_Cam_Test.JDO_PAUI import jdo_pip
from Camera_Test_Logic.MAM_Cam_Test.Camera_PIP_En_Ds import main


class Test_Mam_cam(unittest2.TestCase):

    def test_pip_on(self):
        pip = "ON"
        u_fps = 30
        pip_s = jdo_pip.jdo_run(pip)
        print(pip_s)
        time.sleep(3)

        ver_pip = main()
        print(ver_pip)
        self.assertEqual(pip_s.upper(), 'PIP-'+ver_pip)
    def test_pip_off(self):
        pip = "OFF"
        u_fps = 30
        pip_s = jdo_pip.jdo_run(pip)
        print(pip_s)
        time.sleep(3)

        ver_pip = main()
        print(ver_pip)
        self.assertEqual(pip_s.upper(), 'PIP-'+ver_pip)


if __name__ == '__main__':
    unittest2.main()
