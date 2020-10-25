from src import config
from src import vision, driving, imageProcessing, manual_movement

import cv2

parser = config.config()


def automotive_movement():

    cv2.namedWindow("Processed")

    image_thread = vision.imageCapRS2()
    robot = driving.serialCom()

    while True:

        depth_frame, frame = image_thread.getFrame()
        ballCnts, basketCnts = imageProcessing.getContours(frame)

        if len(basketCnts) > 0:
            basketX, basketY, w, h = imageProcessing.detectObj(frame, ballcnts, False)

        if len(ballCnts) > 0 :
            ballX, ballY = imageProcessing.detectObj(frame, ballcnts)
            if ballX != -1:
                middle_px = parser.get('Cam', 'Width') / 2 - 10
                robot.omniMovement(20, middle_px, int(x), int(y))
            else:
                robot.right(10)

        #angle = obj1.calcDirectionAngle(90, x, y)
        # if x != -1 and depth_frame is not None:
        #     print("distance: ", depth_frame.get_distance(int(x), int(y)))

        cv2.imshow('Processed', frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break

    image_thread.setStopped(False)
    robot.setStopped(False)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if parser.get("Params", "manual"):
        manual_movement()
    else:
        automotive_movement()

