import cv2
import webcamPy as wpy
import sys

w = wpy.Webcam()

# returns the current value of the property in the range [0,100]
def getCurrentVal(prop):
    range_ = w.getCameraControlProperty(prop)
    if len(range_) != 0:
        print('range_ = %s' % repr(range_))
        currentVal, minVal, maxVal, defaultVal = range_
        val = int(float((currentVal - minVal) / (maxVal - minVal)) * 100)
        print('getCurrentVal(%s) = %d' % (prop, val))
        return val
    else:
        return 50

def onTrackbar(val, prop, winname):
    val = cv2.getTrackbarPos(prop, winname)
    val = (float(val) / 100) # convert to [0, 1]
    range_ = w.getCameraControlProperty(prop)
    if len(range_) != 0:
        print('range_ = %s' % repr(range_))
        currentVal, minVal, maxVal, defaultVal = range_
        val = val * (maxVal - minVal) + minVal # map [0,1] to range [minVal, maxVal]
        print('setting \"%s\" to %d' % (prop, int(val)))
        if not w.setCameraControlProperty(prop, int(val)):
            print('Unable to set property %s' % prop)

winname = 'video'
win = cv2.namedWindow(winname)
props = ['brightness', 'zoom', 'pan', 'tilt']
if not w.open(1280, 720, 30.0, "YUY2"):
    print('cannot open panacast camera')
    sys.exit(1)

# we need to get the lambda from a function so that the scope of x is limited to this function
# otherwise, x will be bound to the last value specified
def makeFunc(prop, winname): 
    return lambda x: onTrackbar(x, prop, winname)

for prop in props:
    cv2.createTrackbar(prop, winname, getCurrentVal(prop), 100,  makeFunc(prop, winname))
        
while True:
    f = w.getFrame()
    f = cv2.cvtColor(f, cv2.COLOR_YUV2BGR_YUY2)
    cv2.imshow(winname, f)
    k = cv2.waitKey(30)
    if k == 27 or k == ord('q'):
        break

