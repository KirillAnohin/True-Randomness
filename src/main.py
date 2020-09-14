import sys
import termios
import tty

from src import calibration, config
from functools import partial

from src import vision, driving
import cv2

parser = config.config()


def calibrate():
    if parser.get("Params", "Calibrate"):
        calibration.calibration()
    else:
        pass


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch


def gs():
    obj1 = driving.SerialCom(10)
    while True:
        suund = getch()
        print(suund)
        if suund == 'w':
            print("WWWWWWW")
            obj1.forward()
        elif suund == 's':
            print("SSSSSSSSS")
            obj1.reverse()
        elif suund == 'd':
            print("DDDDDDD")
            obj1.right()
        elif suund == 'a':
            print("AAAAAAAAA")
            obj1.left()
        elif suund == 'p':
            print("Break")
            break

    obj1.__del__()

if __name__ == "__main__":
    calibrate()
