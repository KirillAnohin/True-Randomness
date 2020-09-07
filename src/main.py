from src import vision
import cv2


def execute():
    image_thread = vision.imageCapRS2()

    while True:
        frame = image_thread.getFrame()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.imshow("frame", frame)
        k = cv2.waitKey(1)
        if k == ord("q"):
            image_thread.setStopped(False)
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    execute()
