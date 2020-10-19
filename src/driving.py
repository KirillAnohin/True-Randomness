import sys
import threading
import time
import serial
import serial.tools.list_ports


class serialCom:

    def commandThread(self):
        while self.running:

            drive = ("sd:" + str(self.speed[0]) + ":" + str(self.speed[1]) + ":" + str(self.speed[2]) + "\r\n")
            throw = ("d:" + str(self.throwSpeed) + "\r\n")

            print(drive)

            self.ser.write(drive.encode("utf-8"))

            time.sleep(0.002)

            self.ser.write(throw.encode("utf-8"))

            while self.ser.inWaiting() > 0:
                self.ser.read()

    def __init__(self, port):
        self.port = ""
        self.availablePorts(port)
        self.running = True
        self.speed = [0, 0, 0]
        self.throwSpeed = 0
        self.w = threading.Thread(name='commandThread', target=self.commandThread)
        self.ser = serial.Serial(('/dev/' + self.port), 115200, timeout=0.01)
        print(self.ser.name)
        self.w.start()

    def gs(self):
        self.ser.write('gs\r\n'.encode("utf-8"))
        response = self.ser.read(20).decode("utf-8")
        return response

    def availablePorts(self, port):
        try:
            ports = serial.tools.list_ports.comports()
            for p in ports:
                print("a")
                if p == port:
                    self.port = port
        except Exception as e:
            print(e)
            sys.exit()

    # sd:left:back:right
    def forward(self, speed):
        self.speed = [speed, 0, -speed]

    def reverse(self, speed):
        self.speed = [-speed, 0, speed]

    def left(self, speed):
        self.speed = [-speed, -speed, -speed]

    def right(self, speed):
        self.speed = [speed, speed, speed]

    def move(self, speed):
        self.speed = [speed[0], speed[1], speed[2]]

    def startThrow(self, speed):
        self.throwSpeed = speed

    def stopThrow(self):
        self.throwSpeed = 0

    def __del__(self):
        self.speed = [0, 0, 0]
        self.throwSpeed = 0
        self.running = False
        self.ser.close()
