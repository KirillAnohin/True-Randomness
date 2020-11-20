import cv2

from src import driving

ThrowSpeed = 200
Speed = 10

def manual_movement():

    cv2.namedWindow("Controller")
    obj1 = driving.serialCom()

    while True:
        k = cv2.waitKey(1) & 0xFF

        if k == ord("w"):
            print("Forward")
            obj1.moveVertical(Speed)
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
        elif k == ord("r"):
            print("Stop throw")
            obj1.stopThrow()
        elif k == ord("q"):
            print("Break")
            break

    obj1.setStopped(False)
    cv2.destroyAllWindows()
