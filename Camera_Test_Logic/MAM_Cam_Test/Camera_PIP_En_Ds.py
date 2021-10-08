import cv2
import numpy as np
import queue
# from matplotlib import pyplot as plt
import threading
import time
import os

human_count = 0
hsc = 0
xp = 945
yp = 525
wp = 320
hp = 180


###########################################Clean Post Execution###########################
def clean():
    dir = os.getcwd()
    fln = os.listdir(dir)
    for itm in fln:
        if itm.endswith('.png'):
            os.remove(itm)
    print("Done!")


##################################logic to compare Peopleface###############################
def mse(imageA, imageB):
    # cv2.imshow('image1', imageA)
    # cv2.imshow('image2', imageB)
    image1 = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    image2 = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(image1, None)
    kp2, des2 = sift.detectAndCompute(image2, None)
    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    # Apply ratio test
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])
    # cv.drawMatchesKnn expects list of lists as matches.
    img3 = cv2.drawMatchesKnn(image1, kp1, image2, kp2, good, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    # cv2.imshow('compare', img3)

    # cv2.waitKey(0)
    g = len(good)
    print(g)
    if g >= 15:
        return "MATCHED"
    else:
        return "NOT-MATCHED"


# cv2.destroyAllWindows()


def compimages(hsc, face_count):
    # test image
    print('hsc:-', hsc)
    print('face-count:-', face_count)
    # global image1, image2
    if hsc == 0 and face_count == 1:
        imageA = cv2.imread('humanviewt0.png')
        imageB = cv2.imread('Faceview0.png')
    elif hsc == 1 and face_count > 1:
        imageA = cv2.imread('humanviewt0.png')
        imageB = cv2.imread('Faceview0.png')
    elif hsc == 0 and face_count > 1:
        imageA = cv2.imread('humanviewt0.png')
        imageB = cv2.imread('Faceview0.png')
    elif hsc == 0 and face_count == 0:
        imageA = cv2.imread('pipview0.png')
        imageB = cv2.imread('Faceview0.png')
    else:
        imageA = cv2.imread('humanviewt0.png')
        imageB = cv2.imread('Faceview0.png')

    reslt = mse(imageA, imageB)
    return reslt


#######################################End of logic to compare people face########################################

def pipnoface(person, quen):
    duration = 10
    start_time = time.time()
    global pt, pip, loc_roi_col
    print('program-2 starting')
    capture_pip = False
    img = cv2.imread('Camview-noppl0.png')
    # img_rgb = cv2.imread('Camview-noppl0.png')
    img_rgb = img.copy()
    # ret, img = cap.read()
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    template = cv2.imread('pipview0.png', 0)

    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

    threshold = 0.8
    loc = np.where(res >= threshold)
    count = 0
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        # global pt, loc_roi_col
        """loc_roi_gray=img_gray[pt[1]:pt[1] + h, pt[0]:pt[0] + w]"""
        capture_pip = True
        count += 1
        """cv2.putText(img_rgb, 'person-' + str(count), (pt[0] - 10, pt[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)"""

    print(count)
    if capture_pip is True and count <= 160:
        pip = 'ON'
        loc_roi_col = img_rgb[pt[1]:pt[1] + h, pt[0]:pt[0] + w]
        cv2.rectangle(img_rgb, (xp, yp), (xp + wp, yp + hp), (0, 255, 255), 2)
        cv2.putText(img_rgb, 'PIP:-' + pip + '-' + str(person), (xp + 20, yp + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        # cv2.imshow("Captured", img_rgb)

        # cv2.imshow("Captured-PIP", loc_roi_col)
        # cv2.waitKey(0)
    elif capture_pip is True and count > 160:
        pip = "OFF"
        loc_roi_col = img_rgb[pt[1]:pt[1] + h, pt[0]:pt[0] + w]
        cv2.rectangle(img_rgb, (xp, yp), (xp + wp, yp + hp), (0, 0, 255), 2)
        cv2.putText(img_rgb, 'PIP-View:-' + pip, (pt[0] + 20, pt[1] + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        # cv2.imshow("Captured-", img_rgb)

        # cv2.imshow('Not a PIP', loc_roi_col)
    cv2.imshow("Result:", img_rgb)

    cv2.imshow('PIP=' + pip, loc_roi_col)
    key = cv2.waitKey(30) & 0xFF
    time.sleep(10)
    current_time = time.time()
    elapsed_time = current_time - start_time

    # if elapse time reached duration set or the `q` key was pressed, break from the loop
    if elapsed_time >= duration or key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
    quen.put(pip)


def pipvthface(quey):
    global cc
    duration = 10
    start_time = time.time()
    faceb_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    # eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml")
    face_cascade = cv2.CascadeClassifier(cv2.data.lbpcascades + "lbpcascade_frontalface.xml")
    body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "HS.xml")
    face_count = 0
    detect_c = 0
    hsc = 0
    xp = 945
    yp = 525
    wp = 320
    hp = 180
    img1 = cv2.imread('Camview-ppl0.png')
    nm_img1 = img1.copy()

    img2 = cv2.imread('pipview0.png')
    roip_color = img1[yp:yp + hp, xp:xp + wp]
    # height,width,depth = im.shape
    y, x, _ = img1.shape
    print(y, x)
    mask = np.zeros((y, x), np.uint8)
    rect_contur = cv2.rectangle(img1, (xp, yp), (xp + wp, yp + hp), (0, 0, 0), -1)

    img = cv2.bitwise_not(img1, img1, mask=mask)
    cv2.imwrite('Camview-maskpip' + str(hsc) + ".png", img)

    template = cv2.imread('pipview0.png')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bodies = body_cascade.detectMultiScale(gray, 1.2, 5)
    for (bx, by, bw, bh) in bodies:
        print('face-detected-body-Part')
        face_count += 1
        while face_count == 1:
            cv2.rectangle(img, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)
            roi_gray = gray[by:by + bh, bx:bx + bw]
            roi_color = img[by:by + bh, bx:bx + bw]
            cv2.imwrite('Faceview' + str(hsc) + ".png", roi_color)
            # cv2.imshow('Faceview', roi_color)

            break

    print(face_count)
    if face_count == 0:
        faces = face_cascade.detectMultiScale(template)
        print('Entering-bodyof-PIP-Part')
        for (x, y, w, h) in faces:
            cv2.rectangle(nm_img1, (xp, yp), (xp + wp, yp + hp), (255, 0, 0), 2)

            bp_roi_color = nm_img1[yp:yp + hp, xp:xp + wp]
            cv2.imwrite('Faceview' + str(hsc) + ".png", bp_roi_color)
            # cv2.imshow('Faceview-temp', bp_roi_color)
            hsc += 1
    elif hsc == 0 and face_count == 1:
        cc = 0
        print("entering-body-complete-image")
        bodyhs = face_cascade.detectMultiScale(template)
        for (x, y, w, h) in bodyhs:
            cv2.rectangle(template, (x, y), (x + w, y + h), (255, 0, 0), 2)
            p_roi_color = template[y:y + h, x:x + w]
            cv2.imwrite('Faceview' + str(0) + ".png", p_roi_color)
            # cv2.imshow('Faceview-1', p_roi_color)
            cc += 1
        print(cc)
    elif hsc > 0 or face_count > 0:
        print('Nobody satisfied entering-final else in-body')
        faces1 = face_cascade.detectMultiScale(img1)
        for (x, y, w, h) in faces1:
            cv2.rectangle(nm_img1, (xp, yp), (xp + wp, yp + hp), (192, 192, 192, 0.0), 2)
            t_roi_color = nm_img1[yp:yp + hp, xp:xp + wp]
            cv2.imwrite('Faceview' + str(hsc) + ".png", t_roi_color)
            # cv2.imshow('Faceview', t_roi_color)

        detect_c += 1
    # cv2.imshow("finalresult", nm_img1)
    if detect_c == 0 and face_count == 0:
        facesf = face_cascade.detectMultiScale(nm_img1)
        print('entr-no-body-case')
        # cv2.imshow("finalresult",nm_img1)
        temp_fc = 0
        for (x, y, w, h) in facesf:
            cv2.rectangle(nm_img1, (x, y), (x + w, y + h), (192, 192, 192), 2)
            ts_roi_color = nm_img1[y:y + h, x:x + w]
            cv2.imwrite('Faceview' + str(hsc) + ".png", ts_roi_color)
            # cv2.imshow('Faceview-2', ts_roi_color)
            temp_fc += 1

    elif detect_c == 0 and cc == 0:
        print('Running-final-else')
        faces2 = faceb_cascade.detectMultiScale(nm_img1)
        for (x, y, w, h) in faces2:
            cv2.rectangle(nm_img1, (xp, yp), (xp + wp, yp + hp), (0, 255, 255), 2)
            roifp_color = nm_img1[yp:yp + hp, xp:xp + wp]
            cv2.imwrite('Faceview' + str(hsc) + ".png", roifp_color)

    comp = compimages(hsc, face_count)
    if comp == "MATCHED":
        PIP = "ON"
        cv2.rectangle(nm_img1, (xp, yp), (xp + wp, yp + hp), (0, 255, 0,), 2)
        cv2.putText(nm_img1, 'PIP-View:-' + 'pip', (xp + 20, yp + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        PIP = "OFF"
        cv2.rectangle(nm_img1, (xp, yp), (xp + wp, yp + hp), (0, 0, 255,), 2)
        cv2.putText(nm_img1, 'PIP-View:-' + 'no-pip', (xp + 20, yp + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.imshow('Capture-result', nm_img1)
    key = cv2.waitKey(20) & 0xff
    time.sleep(10)
    current_time = time.time()
    elapsed_time = current_time - start_time
    #key = cv2.waitKey(10) & 0xFF


    # if elapse time reached duration set or the `q` key was pressed, break from the loop
    if elapsed_time >= duration or key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
    quey.put(PIP)


# cv2.destroyAllWindows()


# cap = cv2.imread('man.jpg')
def pip_main(cap, human_LBP):
    duration = 15
    start_time = time.time()
    frame_count = 0
    false_frame = 0
    while True:
        # img=cv2.VideoCapture(0)
        ret, img = cap.read()
        # img= imutils.resize(img, height=1280,width=720)
        img = cv2.resize(img, (1280, 720))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        human = human_LBP.detectMultiScale(gray, 1.3, 3)

        human_count = 0
        hsc = 0
        xp = 945
        yp = 525
        wp = 320
        hp = 180

        for (hx, hy, hw, hh) in human:
            #cv2.rectangle(img, (hx, hy), (hx + hw, hy + hh), (255, 255, 255), 2)
            roih_gray=gray[hy:hy + hh, hx:hx + hw]
            roih_col = img[hy:hy + hh, hx:hx + hw]
            eyes = eye_cascade.detectMultiScale(roih_gray)
            eye_count = 0
            for (ex, ey, ew, eh) in eyes:
                eye_count += 1
                if eye_count>=1:
                    cv2.rectangle(img, (hx, hy), (hx + hw, hy + hh), (255, 255, 255), 2)
                    human_count += 1
                    cv2.imwrite('humanviewt' + str(hsc) + ".png", roih_col)
                    cv2.imshow('humanview1', roih_col)

        if human_count >= 1:
            roip_gray = gray[yp:yp + hp, xp:xp + wp]
            cv2.imwrite('Camview-ppl' + str(hsc) + ".png", img)
            # roip_gray = gray[yp:yp + hp, xp:xp + wp]
            roip_color = img[yp:yp + hp, xp:xp + wp]
            cv2.imwrite('pipview' + str(hsc) + ".png", roip_color)
            print('person detected no of time:' + str(human_count))

            """text = "Switch View-IZ-VD"
            col = (100, 255, 0)
            cv2.putText(roip_color, text + "-" + str(hsc), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, col, 2)
            cv2.imshow("Captured-IZ-VD", roip_color)"""
        else:
            false_frame += 1
            if false_frame > 10:
                cv2.imwrite('Camview-noppl' + str(hsc) + ".png", img)
                roip_gray = gray[yp:yp + hp, xp:xp + wp]
                roip_color = img[yp:yp + hp, xp:xp + wp]
                cv2.imwrite('pipview' + str(hsc) + ".png", roip_color)
            # cv2.rectangle(img, (xp, yp), (xp + wp, yp + hp), (0, 255, 255), 2)
            print('NO person in frame:' + str(frame_count))

        cv2.imshow('img', img)
        frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - start_time
        key = cv2.waitKey(20) & 0xFF
        # if elapse time reached duration set or the `q` key was pressed, break from the loop
        if elapsed_time >= duration or key == ord('q'):
            break
        # k = cv2.waitKey(30) & 0xff
        # if k == 27:
        # breakq
    cap.release()
    cv2.destroyAllWindows()
    return human_count, img


if __name__ == '__main__':
    PIP_X = [470, 945]
    PIP_Y = [260, 525]
    PIP_w = [160, 318]
    PIP_h = [90, 178]
    warmup_frame = 200
    capture_frame = 0
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt.xml")
    # eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    human_LBP = cv2.CascadeClassifier(cv2.data.lbpcascades + "lbpcascade_frontalface.xml")
    body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "HS.xml")
    cap = cv2.VideoCapture(1)
    detect, img = pip_main(cap, human_LBP)
    print(detect)
    # vs = cv2.VideoCapture(1)
    que = queue.Queue()
    Thread_list = [2]
    # time.sleep(15)
    t1 = threading.Thread(target=pipvthface, args=(que,))
    t2 = threading.Thread(target=pipnoface, args=(detect, que))
    if detect >= 1:
        t1.start()
        t1.join()

    else:
        t2.start()
        t2.join()
    result = que.get()
    print(result)
    # que.empty()
clean()
# cv2.destroyAllWindows()
