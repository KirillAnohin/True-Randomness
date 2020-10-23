import cv2

import driving


def manual_movement():
    cv2.namedWindow("Controller")
    obj1 = driving.serialCom()
    throwSpeed = 200
    speed = 10
    while True:
        k = cv2.waitKey(1)
        if k == ord("w"):
            print("Forward")
            obj1.moveVertical(speed)
        elif k == ord("s"):
            print("Backward")
            obj1.reverse(speed)
        elif k == ord("d"):
            print("Right")
            obj1.right(speed)
        elif k == ord("a"):
            print("Left")
            obj1.left(speed)
        elif k == ord("t"):
            print("Throw")
            obj1.startThrow(throwSpeed)
        elif k == ord("r"):
            print("Stop throw")
            obj1.stopThrow()
        elif k == ord("q"):
            print("Break")
            break

    obj1.setStopped(False)
