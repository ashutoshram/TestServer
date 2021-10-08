import unittest

from Camera_Test_Logic.PYTH_Cam_Test.Camera_IZ_VD import cameraiz_vd
from Camera_Test_Logic.PYTH_Cam_Test.cam_ppl_count import ppl_dct
from Camera_Test_Logic.PYTH_Cam_Test.Camera_PIZ import camerapiz_vd
from Camera_Test_Logic.PYTH_Cam_Test import Get_Camera_Supported_Resln
from Camera_Test_Logic.PYTH_Cam_Test import Video_Qual_Test
from Camera_Test_Logic.PYTH_Cam_Test import CameraPTZ
from Camera_Test_Logic.PYTH_Cam_Test.JDO_PAUI import iz_vd_check
import json

Resolution_py = ['640.0x360.0', '960.0x540.0', '1280.0x720.0', '1920.0x1080.0', '3840.0x1080.0', '4800.0x1200.0']
Resolution_mam = ['640.0x360.0', '960.0x540.0', '1280.0x720.0', '1920.0x1080.0']


class Test_Pytcam(unittest.TestCase):
    def test_cameraiz_vd(self):
        izs=iz_vd_check.jdo_run()
        print(izs)
        if izs=='iz-ON':
            total = cameraiz_vd()
            self.assertGreater(total, 1)

    def test_camera_piz(self):
        total1 = camerapiz_vd()
        self.assertGreater(total1, 1)

    def test_ppl_count(self):
        count = ppl_dct()
        self.assertGreaterEqual(count, 1)

    def test_Camera_supported_resolution(self):
        pyt_cam_res = Get_Camera_Supported_Resln.cam_res()
        resolution = json.loads(pyt_cam_res)
        res = [i for i in resolution if resolution[i] == "Supported"]
        self.assertListEqual(Resolution_py, res)

    def test_Video_Qual_Test(self):

        fps, latency = Video_Qual_Test.Camera_FPS_Latensy.fps_latency()
        vq = Video_Qual_Test.main(fps, latency)
        print(vq)
        fps1 = "{:.2f}".format(fps)
        if float(fps1) > 29.30:
            fps1 = 30
            rfps = Video_Qual_Test.runningfps.run_fps(fps1)
            print(rfps)
            self.assertEqual(float(rfps), float(fps1))
        elif float(fps1) > 14.30:
            fps1 = 15
            rfps = Video_Qual_Test.runningfps.run_fps(fps1)
            print(rfps)
            self.assertEqual(float(rfps), float(fps1))
        else:
            fps1 = fps
            rfps = Video_Qual_Test.runningfps.run_fps(fps1)
            print(rfps)
            self.failIf(15.0 == rfps == 30.0)

    def test_jpc50_ptz(self):
        ptz = CameraPTZ.jpc_ptz()
        self.assertGreaterEqual(ptz, 5)


if __name__ == '__main__':
    unittest.main()
