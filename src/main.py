from src import config
from src import vision, driving, imageProcessing, manual_movement

import cv2

parser = config.config()


def automotive_movement():
    cv2.namedWindow("Processed")
    image_thread = vision.imageCapRS2()
    obj1 = driving.serialCom()

    while True:
        depth_frame, frame = image_thread.getFrame()
        cnts = imageProcessing.getContours(frame)
        cv2.imshow('Processed', frame)
        if len(cnts) > 0:
            x, y = imageProcessing.detectObj(frame, cnts)
            if x > 210 and x < 480 :
                obj1.move([0,0,0])
            elif x > parser.get('Cam', 'Width') / 2 + 30:
                obj1.right(4)
            elif x < parser.get('Cam', 'Width') / 2 - 30:
                obj1.left(4)
        else:
            obj1.left(4)
        k = cv2.waitKey(1)
        if k == ord("q"):
            break

    image_thread.setStopped(False)
    obj1.setStopped(False)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if parser.get("Params", "manual"):
        manual_movement()
    else:
        automotive_movement()

