import math
import threading
import time
import serial


class serialCom:

    def commandThread(self):
        while self.running:
            time.sleep(0.005)
            drive = ("sd:" + str(self.speed[0]) + ":" + str(self.speed[1]) + ":" + str(self.speed[2]) + "\r\n")
            throw = ("d:" + str(self.throwSpeed) + "\r\n")
            print(drive + throw)

            self.ser.write(drive.encode("utf-8"))
            time.sleep(0.005)
            self.ser.write(throw.encode("utf-8"))

            while self.ser.inWaiting() > 0:
                self.ser.read()

    def __init__(self):
        self.running = True
        self.forward_movement_angle = 90
        self.middle_wheel_angle = 0
        self.right_wheel_angle = 120
        self.left_wheel_angle = 240
        self.throwSpeed, self.speed = 100, [0, 0, 0]
        self.w = threading.Thread(name='commandThread', target=self.commandThread)
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.01)
        print(self.ser.name)
        self.w.start()

    def gs(self):
        self.ser.write('gs\r\n'.encode("utf-8"))
        response = self.ser.read(20).decode("utf-8")
        print(response)

    # sd:right:middle:left
    def forward(self, speed):
        self.speed = [-speed, 0, speed]

    def reverse(self, speed):
        self.speed = [speed, 0, -speed]

    def left(self, speed):
        self.speed = [-speed, -speed, -speed]

    def right(self, speed):
        self.speed = [speed, speed, speed]

    def move(self, speed):
        self.speed = [speed[0], speed[1], speed[2]]

    def startThrow(self, speed):
        self.throwSpeed = speed

    def stopThrow(self):
        self.throwSpeed = 100

    def stopMoving(self):
        self.speed = [0, 0, 0]

    def calcDirectionAngle(self, robotDirectionAngle, middle_px, X, Y):
        robotDirectionAngle = int(math.degrees(math.atan((middle_px-X) / Y) + robotDirectionAngle))
        return robotDirectionAngle

    def wheelLinearVelocity(self, robotSpeed, wheelAngle, robotDirectionAngle, middle_px=None, X=None, Y=None):
        if Y is not None and Y != 0:
            robotDirectionAngle = self.calcDirectionAngle(robotDirectionAngle, middle_px, X, Y)
            wheelLinearVelocity = robotSpeed * math.cos(math.radians(robotDirectionAngle - wheelAngle))
        else:
            wheelLinearVelocity = robotSpeed * math.cos(math.radians(robotDirectionAngle - wheelAngle))
        return int(wheelLinearVelocity)

    def omniMovement(self, speed, middle_px, X=None, Y=None):
        self.speed[0] = self.wheelLinearVelocity(-speed, self.right_wheel_angle, self.forward_movement_angle, middle_px, X, Y)
        self.speed[1] = self.wheelLinearVelocity(-speed, self.middle_wheel_angle, self.forward_movement_angle, middle_px, X, Y)
        self.speed[2] = self.wheelLinearVelocity(-speed, self.left_wheel_angle, self.forward_movement_angle, middle_px, X, Y)

    def setStopped(self, stopped):
        self.running = stopped
        time.sleep(0.2)
        self.throwSpeed, self.speed = 0, [0, 0, 0]
        self.ser.close()

