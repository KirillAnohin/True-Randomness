import cv2
import time

from src import serialCom

ThrowSpeed = 50
Speed = 10


def main():
    cv2.namedWindow("Controller")
    obj1 = serialCom.serialCom()

    while True:
        k = cv2.waitKey(1) & 0xFF

        if k == ord("w"):
            print("Forward")
            obj1.forward(Speed)
        elif k == ord("s"):
            print("Backward")
            obj1.reverse(Speed)
        elif k == ord("d"):
            print("Right")
            obj1.right(Speed)
        elif k == ord("a"):
            print("Left")
            obj1.left(Speed)
        elif k == ord("t"):
            print("Throw")
            obj1.startThrow(ThrowSpeed)
        elif k == ord("l"):
            print("robot stop")
            obj1.stopMoving()
        elif k == ord("r"):
            print("Stop throw")
            obj1.stopThrow()
        elif k == ord("q"):
            print("Break")
            break

    obj1.stopMoving()
    time.sleep(0.2)
    obj1.setStopped(False)
    cv2.destroyAllWindows()
