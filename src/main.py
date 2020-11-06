from src import config
from src import vision, driving, imageProcessing, manual_movement
from simple_pid import PID

import cv2

parser = config.config()


def automotive_movement():

    cv2.namedWindow("Processed")

    image_thread = vision.imageCapRS2()
    robot = driving.serialCom()
    PID.output_limits(-30, 30)
    middle_px = parser.get('Cam', 'Width') / 2 + 12

    while True:

        depth_frame, frame = image_thread.getFrame()
        ballCnts, basketCnts = imageProcessing.getContours(frame)

        if len(basketCnts) > 0:
            basketX, basketY, w, h = imageProcessing.detectObj(frame, basketCnts, False)

        if len(ballCnts) > 0:
            ballX, ballY = imageProcessing.detectObj(frame, ballCnts)
            distance = imageProcessing.getDistance(depth_frame, ballX, ballY)

            if distance <= 10:
                break

            if ballX != -1:
                PID()
                robot.omniMovement(20, middle_px, ballX, ballY)
            else:
                robot.right(10)

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

