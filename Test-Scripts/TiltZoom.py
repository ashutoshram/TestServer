
production = True
debug = False 
if not production:
    import AbstractTestClass as ATC
    import webcamPy as wpy
else:
    import eos.scripts.AbstractTestClass as ATC
    import eos.scripts.webcamPy as wpy

def dbg_print(*args):
    if debug: 
        print("".join(map(str, args)))

class TiltZoom(ATC.AbstractTestClass):

    def __init__(self):
        self.TiltZoomTest = None

    def get_args(self):
       return ['tilt','zoom']

    def run(self, args, q, results):
        self.TiltZoomTest = TiltZoomTester()
        return self.TiltZoomTest.test(args, q, results)

    def get_progress(self):
        if self.TiltZoomTest is None:
            return 0
        return self.TiltZoomTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "Tilt and Zoom Test"
    
    def is_done(self):
        if self.TiltZoomTest is None:
            return False
        else:
            if self.TiltZoomTest.progress() == 100:
                return True
            else:
                return False

    def generate_report(self):
        return self.TiltZoomTest.results()


class TiltZoomTester():

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0 
        self.cam = wpy.Webcam()
        #print("hello")
        if not self.cam.open(3840, 1080, 30.0, "YUY2"):
            print("PanaCast cannot be opened!!")
        print("opened panacast device")

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    # verifies if given parameter is set correctly and puts result in err_code
    def verify(self,control,num):
        prop = self.cam.getCameraControlProperty(control)
        #print(prop)
        if prop[0]== num:
            self.err_code[control+'set:'+str(num)] = 0
        else:
            self.err_code[control+'set:'+str(num)] = -1
       #print(self.err_code)

    def test_drive(self,args):
        for z in range(len(args)-1):
            x = self.cam.getCameraControlProperty(args[z])
            #print(int(x[2])+1)
            for y in range(x[1],int(x[2]+1)):
                self.cam.setCameraControlProperty(args[z],y)
                self.verify(args[z],y)


    # iterates through and tests all available tilt values, calling on verify() to check 
    '''
    def test_tilt(self, args):
        if 'tilt' in args:
            x = self.cam.getCameraControlProperty('tilt')
            print(int(x[2])+1)
            for y in range(x[1],int(x[2]+1)):
                self.cam.setCameraControlProperty('tilt',y)
                self.verify('tilt',y)
        else:
            pass

    # iterates through and tests all available zoom values, calling on verify() to check 
    def test_zoom(self,args):
        if 'zoom' in args:
            x = self.cam.getCameraControlProperty('zoom')
            print(int(x[2])+1)
            for y in range(x[1],int(x[2]+1)):
                self.cam.setCameraControlProperty('zoom',y)
                self.verify('zoom',y)
        else:
            pass
   '''
   #  main driver function to run both tets, as well as update progress
    def test(self, args, q, results):
        '''
    	x = self.cam.getCameraControlProperty('tilt')
    	y=self.cam.getCameraControlProperty('zoom')
    	print('original:')
    	print(x)
        print(y)
        test_tilt(args)
        test_zoom(args)
        self.cam.setCameraControlProperty('tilt',5)
        self.cam.setCameraControlProperty('zoom', 10)
        x1 = self.cam.getCameraControlProperty('tilt')
        y1=self.cam.getCameraControlProperty('zoom')
        print(x1)
        print(y1)
        '''
        self.test_drive(args)

        self.cam.setCameraControlProperty('zoom', 0)
        self.cam.setCameraControlProperty('tilt', 0)
        self.cam.setCameraControlProperty('pan', 0)
        zoomVal = 0
        tiltVal = -20
        panVal = -84
        for x in range(0,2):
            zoomVal = zoomVal + 15
            self.cam.setCameraControlProperty('zoom', zoomVal)
            self.progress_percent += 10
            q.put(self.progress_percent)
            q.task_done()
        for y in range(0,3):
            self.cam.setCameraControlProperty('tilt', tiltVal)
            self.progress_percent += 5
            q.put(self.progress_percent)
            q.task_done()
            tiltVal += 10
        self.cam.setCameraControlProperty('tilt', 0)
        for z in range(0,7):
            self.cam.setCameraControlProperty('pan', panVal)
            self.progress_percent += 5
            self.put(self.progress_percent)
            q.task_done()
            panVal += 21
        self.cam.setCameraControlProperty('zoom', 0)
        self.cam.setCameraControlProperty('tilt', 0)
        self.cam.setCameraControlProperty('pan', 0)
        self.progress_percent += 10
        self.put(self.progress_percent)
        q.task_done()
        print(self.err_code)
        results.put("DONE")
        results.put(self.err_code)
        print(self.err_code)
        return self.err_code

if __name__ == "__main__":
	t = TiltZoom()
	args = t.get_args()
	t.run(args)
	print(t.generate_report())



