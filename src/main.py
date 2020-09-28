from src import calibration, config
from src import vision, driving

import cv2

parser = config.config()


def calibrate():
    if parser.get("Params", "Calibrate"):
        calibration.calibration()
    else:
        pass


def manual_movement():
    cv2.namedWindow("Controller")
    obj1 = driving.serialCom()
    throwSpeed = 1000
    speed = 4
    while True:
        k = cv2.waitKey(1)
        if k == ord("w"):
            print("Forward")
            obj1.forward(speed)
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
        elif k == ord("p"):
            print("Break")
            obj1.__del__()
            break


if __name__ == "__main__":
    calibrate()
    manual_movement()
