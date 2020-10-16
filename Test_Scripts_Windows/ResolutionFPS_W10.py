#python 3.6 
#last updated 6/27 
import cv2 
import numpy as np
import time

production = True
debug = True 
if not production:
    import AbstractTestClass as ATC
    import webcamPy as wpy
else:
    import eos.scripts.AbstractTestClass as ATC
    import eos.scripts.webcamPy as wpy

def dbg_print(*args):
    if debug: 
        print("".join(map(str, args)))

class resolutionFPS(ATC.AbstractTestClass):

    def __init__(self):
        self.ResolutionFPSTest = None

    def get_args(self):
        ResList =[ '4800x1200' ,'640x480','3840x1088','3840x1080','960x544','1280x720','1920x1080']
        return ResList

    def run(self, args, q, results, wait_q):
        self.ResolutionFPSTest = ResolutionFPSTester()
        self.ResolutionFPSTest.test(args,q,results)
        print("ResolutionFPS.run: waiting for wait_q")
        time.sleep(5)
        got = wait_q.get()
        print("ResolutionFPS.run: got %s" % repr(got))


    def get_progress(self):
        if self.ResolutionFPSTest is None:
            return 0
        return self.ResolutionFPSTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "resolutionFPS Test"
    
    def is_done(self):
        if self.ResolutionFPSTest is None:
            return False
        else:
            if self.ResolutionFPSTest.progress() == 100:
                return True
            else:
                return False

    def generate_report(self):
        return self.ResolutionFPSTest.results()

class ResolutionFPSTester():

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0 
        self.cam = wpy.Webcam()
        print("hello")
        print("opened panacast device")
        
    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code
    #function to test FPS, collects frames for 5 seconds, calculates FPS and compares 
    def testFPS(self,fps):
        start= time.time()  #start time of func
        count= 0            
        skip= 10
        while True:
            if( time.time() - start) > 5.0:     #if 5 seconds has passed,then break 
                break
            frame = self.cam.getFrame()          #get frame
            skip -=1
            if skip == 0:                   #after getting 10 frames
                start = time.time()         
                count = 0
                print('starting fps test')
            count+=1

        elapsed = time.time() - start
        calc_fps = float(count) / elapsed
        print('Expected FPS= %f'% fps)
        print('Actual FPS = %f' % calc_fps)
        eps = 1.0
        # if fps difference is >1, its a fail
        abs_diff = abs(calc_fps - fps)
        if abs_diff < eps:
            print('success')
            return 0
        else:
            print('FPS fail')
            return -1
               
    #main driver function to run full test 
    def test(self, args,q,results):
        #dict and lists of all possible values 
        w_h = {4800:1200 ,640:480,3840:1088,3840:1080,960:544,1280:720,1920:1080}
        width = [4800,640,3840,3840,960,1280,1920]
        height= [1200,480,1088,1080,544,720,1080]
        FPS = [15.0,24.0,27.0,30.0]
        ResList =[ '4800x1200' ,'640x480','3840x1088','3840x1080','960x544','1280x720','1920x1080']

        args_ind = []   #contains indeces in width, height where chosen args are located 
        args_length= len(args)
        increment = int(100/(args_length*4)) # increment for progress bar 
        #files which indeces to pull resolution size from,from the user selected parameters 
        for x in range(len(args)):
            if args[x] in ResList:
                print(ResList.index(args[x]))
                args_ind.append(ResList.index(args[x]))

        #main driver code to run the test
        # first for loop iterates through chosen args , 2nd for loop iterates through all possible FPS's
        for x in range(args_length):
            for z in range(0,4):
                print(str(FPS[z])+'FPS') 
                #skips over resolution FPS pairs that aren't supported                
                if (FPS[z] !=15.0 and width[args_ind[x]]==4800) or (width[args_ind[x]]==1920 and FPS[z]==27.0) :
                    print('skipping this test')
                    pass 
                else:
                    if not self.cam.open(width[args_ind[x]] ,height[args_ind[x]],FPS[z], 'YUY2'):
                        print("Can't Open Camera")
                    F = self.cam.getFrame()
                    F = cv2.cvtColor(F, cv2.COLOR_YUV2BGR_YUY2) 
                    string =str(FPS[z])+'FPS'+str(width[args_ind[x]]) +'x'+str(height[args_ind[x]])+'.jpg'
                    cv2.imwrite(string,F)
                    print(string+' file create was successful')
                    h,w,c = F.shape        
                    print('testing: '+str(FPS[z]))   
                    #tests wether resolution of created frame is correct and puts result into err_code  
                    if(h== height[args_ind[x]]) and ( w == width[args_ind[x]]):
                        print(string+' resolution was successful')
                        if self.testFPS(FPS[z])== 0:
                            #good for both
                            self.err_code[string] = 0
                        else:
                            #FPS failed,Res Passed
                            self.err_code[string] = -1
                    elif self.testFPS(FPS[z])== 0:
                        #Res Fail,FPS PASS
                        self.err_code[string] = -1
                    else:
                        #BothFail
                        self.err_code[string] = -1
                self.progress_percent +=increment
                q.put(self.progress_percent)
                print(self.err_code)
        self.progress_percent=100
        q.put(self.progress_percent)
        results.put(self.err_code)
        return self.err_code
        
if __name__ == "__main__":
    t = resolutionFPS()
    args = t.get_args()
    t.run(args)
    print(t.generate_report())
