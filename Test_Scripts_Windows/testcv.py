import cv2

cam = cv2.VideoCapture(0)

brightness = [0, 128, 255]

for b in brightness:
    initial = cam.get(cv2.CAP_PROP_BRIGHTNESS)
    print("Intial brightness:     {}".format(initial))
    print("Setting brightness to: {}".format(b))
    cam.set(cv2.CAP_PROP_BRIGHTNESS, b)
    actual = cam.get(cv2.CAP_PROP_BRIGHTNESS)
    print("Brightness set to:     {}\n".format(actual))

contrast = [0, 95, 191]

for c in contrast:
    initial = cam.get(cv2.CAP_PROP_CONTRAST)
    print("Intial contrast:     {}".format(initial))
    print("Setting contrast to: {}".format(c))
    cam.set(cv2.CAP_PROP_CONTRAST, c)
    actual = cam.get(cv2.CAP_PROP_CONTRAST)
    print("Contrast set to:     {}\n".format(actual))

saturation = [128, 136, 160, 176, 155]

for sat in saturation:
    initial = cam.get(cv2.CAP_PROP_SATURATION)
    print("Intial saturation:     {}".format(initial))
    print("Setting saturation to: {}".format(sat))
    cam.set(cv2.CAP_PROP_SATURATION, sat)
    actual = cam.get(cv2.CAP_PROP_SATURATION)
    print("Saturation set to:     {}\n".format(actual))

sharpness = [0, 110, 128, 255, 193]

for sh in sharpness:
    initial = cam.get(cv2.CAP_PROP_SHARPNESS)
    print("Intial sharpness:     {}".format(initial))
    print("Setting sharpness to: {}".format(sh))
    cam.set(cv2.CAP_PROP_SHARPNESS, sh)
    actual = cam.get(cv2.CAP_PROP_SHARPNESS)
    print("Sharpness set to:     {}\n".format(actual))

white_balance = [0, 5000, 6500]

for wb in white_balance:
    initial = cam.get(cv2.CAP_PROP_TEMPERATURE)
    print("Intial white_balance:     {}".format(initial))
    print("Setting white_balance to: {}".format(wb))
    cam.set(cv2.CAP_PROP_TEMPERATURE, wb)
    actual = cam.get(cv2.CAP_PROP_TEMPERATURE)
    print("white_balance set to:     {}\n".format(actual))

cam.release()
