import time

from src import config
from src import vision, serialCom, imageProcessing, utils
from src import manual_movement
from simple_pid import PID

import cv2

parser = config.config()


def automotive_movement():

    cv2.namedWindow("Processed")

    image_thread = vision.imageCapRS2()
    robot = serialCom.serialCom()

    throwerSpeeds = utils.readThrowerFile("../config/measurements.csv")
    middle_px = parser.get('Cam', 'Width') / 2 - 0
    rotateForBasketSpeed = PID(0.15, 0, 0, setpoint=320)
    toBallSpeed = PID(0.3, 0.00001, 0.0001, setpoint=400)
    toBallSpeed.output_limits = (-50, 50)

    iter = 0
    ballX = -1
    basketX = -1
    basket_dist_from_centerX = 320
    distBuffer = []
    throwing = False
    counter = 0

    while True:

        depth_frame, frame = image_thread.getFrame()
        ballCnts, basketCnts = imageProcessing.getContours(frame)

        if counter > 60:
            counter = 0
            throwing = False
            robot.stopThrow()
            robot.stopMoving()

        if len(distBuffer) > 15:
            distBuffer.pop(0)

        if len(basketCnts) > 0:  # BasketCNTS
            basketX, basketY, w, h = imageProcessing.detectObj(frame, basketCnts, False)

            distance = imageProcessing.calc_distance(w)
            if distance > 0:
                distBuffer.append(distance)

            print(basketX, basketY, h, w)
            if basketX > -1:
                basket_dist_from_centerX = middle_px - basketX
            else:
                basket_dist_from_centerX = 320


        if len(ballCnts) > 0:  # BallCNTS
            ballX, ballY = imageProcessing.detectObj(frame, ballCnts)

            if basketX > -1:
                ball_dist_from_centerX = middle_x_pixel - ball_X

        if ballX != -1:

            if throwing:
                if abs(basket_dist_from_centerX) < 2:
                    if abs(ball_dist_from_centerX) < 42:
                        counter += 1
                        robot.forward(40)
                        if counter == 1:
                            if len(distBuffer) > 0:
                                maxdist = max(distBuffer)
                                if maxdist > 0:
                                    speed = utils.throwStrength(maxdist, throwerSpeeds)
                        robot.startThrow(speed)

                    else:
                        X_speed = ball_dist_from_centerX/20
                        if X_speed <= 0:
                            calculated_speed = -min(5+abs(X_speed), 20)
                        else:
                            calculated_speed = min(5 + X_speed, 20)

                        robot.moveVertical(calculated_speed)

                else:
                    robot.rotateAroundBall(int(-rotateForBasketSpeed(basketX)))

            elif ballY > parser.get('Cam', 'Height') - 100 and not throwing:
                throwing = True

            else:
                robot.omniMovement(int(toBallSpeed(ballY)), middle_px, ballX, ballY)

        else:
            iter += 1
            if iter > 3:
                robot.left(10)
                iter = 0

        cv2.imshow('Processed', frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break

    image_thread.setStopped(False)
    robot.stopThrow()
    robot.setStopped(False)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if parser.get("Params", "manual"):
        manual_movement.manual_movement()
    else:
        automotive_movement()
