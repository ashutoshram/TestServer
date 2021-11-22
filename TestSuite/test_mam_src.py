import unittest
from Camera_Test_Logic.MAM_Cam_Test.Camera_IZ_VD import cameraiz_vd
from Camera_Test_Logic.MAM_Cam_Test.Camera_PIZ import camerapiz_vd
from Camera_Test_Logic.MAM_Cam_Test import Get_Camera_Supported_Resln
from Camera_Test_Logic.MAM_Cam_Test import Video_Qual_Test
# from Camera_Test_Logic.MAM_Cam_Test import CameraPTZ
from Camera_Test_Logic.MAM_Cam_Test.JDO_PAUI import jdo_vivid
from Camera_Test_Logic.MAM_Cam_Test import runningfps
from Camera_Test_Logic.MAM_Cam_Test import Camera_FPS_Latensy
import json

Resolution_mam = ['640.0x360.0', '960.0x540.0', '1280.0x720.0', '1920.0x1080.0']


class Test_Mam_cam(unittest.TestCase):

    def test_vq_vivd_off(self):
        vivid = "OFF"
        u_fps = 30
        viv_s = jdo_vivid.jdo_run(vivid)
        print(viv_s)
        if viv_s == 'vivid-off':
            fps, latency = Camera_FPS_Latensy.fps_latency(u_fps)
            vq = Video_Qual_Test.main(fps, latency)
            print(vq)
            fps1 = "{:.2f}".format(fps)
            if float(fps1) > 29.30:
                fps1 = 30
                rfps = runningfps.run_fps(fps1)
                print(rfps)
                self.assertEqual(float(rfps), float(fps1))
            elif float(fps1) > 14.30:
                fps1 = 15
                rfps = runningfps.run_fps(fps1)
                print(rfps)
                self.assertEqual(float(rfps), float(fps1))
            else:
                fps1 = fps
                rfps = runningfps.run_fps(fps1)
                print(rfps)
                self.failIf(15.0 == rfps == 30.0)
            self.assertEqual('Sharp',list(vq['Sharpness'])[0])
            self.assertEqual('No Noise',list(vq['Noise'])[0])
    def test_vq_vivd_on(self):
        vivid = "ON"
        u_fps = 30
        viv_s = jdo_vivid.jdo_run(vivid)
        print(viv_s)
        if viv_s == 'vivid-on':
            fps, latency = Camera_FPS_Latensy.fps_latency(u_fps)
            vq = Video_Qual_Test.main(fps, latency)
            print(vq)
            fps1 = "{:.2f}".format(fps)
            if 29.30 < float(fps1) < 30.3:
                fps1 = 30
                rfps = runningfps.run_fps(fps1)
                print(rfps)
                self.assertEqual(float(rfps), float(fps1))
            elif 14.30 < float(fps1) < 15.3:
                fps1 = 15
                rfps = runningfps.run_fps(fps1)
                print(rfps)
                self.assertEqual(float(rfps), float(fps1))
            else:
                fps1 = round(fps)
                rfps = runningfps.run_fps(fps1)
                print(rfps)
                self.failIf(15.0 <= rfps >= 30.0)
            self.assertEqual('Sharp',list(vq['Sharpness'])[0])
            self.assertEqual('No Noise',list(vq['Noise'])[0])

if __name__ == '__main__':
    unittest.main()
