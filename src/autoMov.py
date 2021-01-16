from datetime import datetime
from enum import Enum, unique, auto
from typing import Tuple, Union

import cv2
from simple_pid import PID

from src import config, vision, imageProcessing
from src.serialCom import serialCom


@unique
class STATE(Enum):
    WAITING = auto()
    FINDING_BALL = auto()
    DRIVING_TO_BALL = auto()
    PICKING_UP_BALL = auto()
    FINDING_BASKET = auto()
    DRIVING_TO_BASKET = auto()
    STARTING_THROWER = auto()
    THROWING_BALL = auto()


class RobotState:
    current: STATE = STATE.WAITING
    target_x: int = 0
    target_y: int = 0
    timer: Union[datetime, None] = 0

    def change_state(self, next_state):
        self.current = next_state
        self.timer = None

    def timer_seconds_passed(self):
        if self.timer is None:
            self.timer = datetime.now()
        return (datetime.now() - self.timer).seconds


def main():
    state = RobotState()

    parser = config.config()

    image_thread = vision.imageCapRS2()
    robot = serialCom()

    middle_px = parser.get('Cam', 'Width') / 2
    toBallSpeed = PID(0.4, 0.00001, 0.0001, setpoint=450)
    toBallSpeed.output_limits = (-50, 50)  # Motor limits

    while True:
        frame = image_thread.getFrame()

        if state.current is STATE.WAITING:
            # waiting
            state.change_state(STATE.FINDING_BALL)
            #
        elif state.current is STATE.FINDING_BALL:
            # finding ball
            ballCnts, basketCnts = imageProcessing.getContours(frame)
            if len(ballCnts) > 0:
                ball_x, ball_y = imageProcessing.detectObj(frame, ballCnts)
                if ball_y > parser.get('Cam', 'Height') - 100:
                    print('found ball')
                    # state.change_state(STATE.PICKING_UP_BALL)
                else:
                    robot.omniMovement(int(toBallSpeed(ball_y)), middle_px, ball_x, ball_y)
            else:
                robot.left(5)
            #
        elif state.current is STATE.PICKING_UP_BALL:
            # picking up ball
            robot.stopMoving()
            robot.setIr(0)
            robot.setServo(50)
            if state.timer_seconds_passed() > 10:
                robot.setServo(-100)  # eject
            # state.change_state(STATE.FINDING_BALL)  # ball disappeared, restart
            elif robot.recive.ir == 1:
                # state.change_state(STATE.FINDING_BASKET)
                pass
            #
        elif state.current is STATE.FINDING_BASKET:
            # finding basket
            ballCnts, basketCnts = imageProcessing.getContours(frame)
            if len(basketCnts) > 0:
                target_x, target_y, w, h = imageProcessing.detectObj(frame, basketCnts, False)
                dist_from_centerX = 320
                if target_x > -1:
                    dist_from_centerX = middle_px - target_x

                if abs(dist_from_centerX) < 3:
                    state.change_state(STATE.DRIVING_TO_BASKET)
                else:
                    if dist_from_centerX > 0:
                        robot.left(int(toBallSpeed(target_y)))
                    else:
                        robot.right(int(toBallSpeed(target_y)))
            else:
                robot.left(5)
            #
        elif state.current is STATE.DRIVING_TO_BASKET:
            # driving to basket
            state.current = STATE.STARTING_THROWER
            #
        elif state.current is STATE.STARTING_THROWER:
            # starting thrower
            robot.startThrow(50)
            if state.timer_seconds_passed() > 2:
                state.change_state(STATE.THROWING_BALL)
            #
        elif state.current is STATE.THROWING_BALL:
            # throwing ball
            robot.setIr(1)
            if state.timer_seconds_passed() > 5:
                robot.setIr(0)
                robot.setServo(0)
                robot.startThrow(0)
                state.change_state(STATE.FINDING_BALL)
            #
        else:
            raise Exception(f'State not implemented in main(): {state.current}')
        pass

        cv2.putText(frame, str(state.current), (10, 30), cv2.FONT_HERSHEY_DUPLEX, 1,
                    cv2.COLOR_YUV420sp2GRAY)
        cv2.imshow('Processed', frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break

    image_thread.setStopped(False)
    robot.stopThrow()
    robot.setStopped(False)
    cv2.destroyAllWindows()
