import cv2
import time

# Load the cascade
#face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
face_lbp = cv2.CascadeClassifier(cv2.data.lbpcascades + "lbpcascade_frontalface.xml")


# To capture video from webcam.
def ppl_dct():
    start_time = time.time()
    duration = 60
    cap = cv2.VideoCapture(1)

    while True:
        # Read the frame
        _, img = cap.read()
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect the faces
        faces = face_lbp.detectMultiScale(gray, 1.3, 3)
        # Draw the rectangle around each face
        count = 0
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            count += 1
            cv2.putText(img, 'person-' + str(count), (x - 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        # Display
        cv2.imshow('img', img)
        current_time = time.time()
        elapsed_time = current_time - start_time
        # Stop if duration time reached
        # print('no-of-person', c)
        k = cv2.waitKey(30) & 0xff
        # if elapse time reached duration set or the `q` key was pressed, break from the loop
        if elapsed_time > duration or k == ord("q"):
            break
    print("No Of person Detected", count)
    cv2.destroyAllWindows()
    return count
    # Release the VideoCapture objectcap.release()





