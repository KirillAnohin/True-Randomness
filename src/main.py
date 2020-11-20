import time

from src import config
from src import vision, driving, imageProcessing, manual_movement
from simple_pid import PID

import cv2

parser = config.config()


# PID.output_limits(-30, 30)


def automotive_movement():
    cv2.namedWindow("Processed")

    image_thread = vision.imageCapRS2()
    robot = driving.serialCom()
    middle_px = parser.get('Cam', 'Width') / 2 + 12
    loops = 0
    basket_dist_from_centerX = 320
    min_speed = 10
    circling_speed = 45
    toBallSpeed = PID(0.3, 0.00001, 0.0001, setpoint=400)
    toBallSpeed.output_limits = (-50, 50)
    throwing = False

    while True:

        depth_frame, frame = image_thread.getFrame()
        ballCnts, basketCnts = imageProcessing.getContours(frame)

        if len(basketCnts) > 0:
            basketX, basketY, w, h = imageProcessing.detectObj(frame, basketCnts, False)
            print(basketX, basketY, h, w)
            if basketX > -1:
                basket_dist_from_centerX = middle_px - basketX
            else:
                basket_dist_from_centerX = 320

        if len(ballCnts) > 0:
            ballX, ballY = imageProcessing.detectObj(frame, ballCnts)

            if ballX != -1 and throwing == False:
                robot.omniMovement(int(toBallSpeed(ballY)), middle_px, ballX, ballY)

            if ballY > parser.get('Cam', 'Height') - 100:
                throwing = True
                X_speed = basket_dist_from_centerX / (320 / (circling_speed - min_speed))
                if X_speed <= 0:
                    calculated_speed = min(min_speed + abs(X_speed), circling_speed)
                else:
                    calculated_speed = -(min(min_speed + X_speed, circling_speed))

                # print("basket from center", basket_dist_from_centerX)
                if 4 > basket_dist_from_centerX > -2:
                    robot.stopMoving()
                    robot.startThrow(180)
                    time.sleep(0.1)
                    robot.forward(40)
                    time.sleep(1.5)
                    robot.stopThrow()
                    throwing = False
                    continue

                robot.rotateAroundBall(calculated_speed)


        else:
            loops += 1
            if loops > 3:
                # diff = middle_px - ballX
                # if diff < 0:
                #     robot.right(10)
                # elif diff > 0:
                #     robot.left(10)
                robot.left(10)
                loops = 0

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
