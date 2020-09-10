from src import vision, driving
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

def gs():
    obj1 = driving.SerialCom(10)
    obj1.forward()
    obj1.__del__()



if __name__ == "__main__":
    #execute()
    gs()
