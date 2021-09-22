import cv2
import time


def run_fps(fps1):
    cap = cv2.VideoCapture(1)
    start_time = time.time()
    duration = 30
    cap.set(5, int(fps1))
    prev_frame_time = 0

    # used to record the time at which we processed current frame
    new_frame_time = 0

    while True:
        ret, frame = cap.read()

        # if video finished or no Video Input
        if not ret:
            break

        # Our operations on the frame come here
        gray = frame

        # resizing the frame size according to our need
        gray = cv2.resize(gray, (1280, 720))

        # font which we will be using to display FPS
        font = cv2.FONT_HERSHEY_SIMPLEX
        # time when we finish processing for this frame
        new_frame_time = time.time()

        # Calculating the fps

        # fps will be number of frame processed in given time frame
        # since their will be most of time error of 0.001 second
        # we will be subtracting it to get more accurate result
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time

        # converting the fps into integer
        fps = int(fps)

        # by using putText function
        color = (100, 255, 0)
        i = 0
        # converting the fps to string so that we can display it on frame
        for ret in frame:
            global fps2
            if int(fps1) == fps:
                fps2 = fps
                i += 1
                cv2.putText(gray, str(fps2), (7, 70), font, 3, color, 3, cv2.LINE_AA)

            else:
                pass

        # puting the FPS count on the frame
        cv2.putText(gray, ('Calculating Running FPS ...' + str(i)), (500, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Display the resulting frame
        cv2.imshow('frame', gray)
        current_time = time.time()
        elapsed_time = current_time - start_time
        key = cv2.waitKey(20) & 0xFF
        # if elapse time reached duration set or the `q` key was pressed, break from the loop
        if elapsed_time >= duration or key == ord('q'):
            break
    cap.release()
    return fps2
    # When everything done, release the capture


cv2.destroyAllWindows()
fp=run_fps('30')
