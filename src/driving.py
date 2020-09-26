import threading
import time
import serial


class serialCom:

    def commandThread(self):
        while self.running:
            time.sleep(0.002)
            print(self.speed)
            self.ser.write(self.message.encode("utf-8"))
            # Buffer cleanup
            while self.ser.inWaiting() > 0:
                self.ser.read()

    def __init__(self):
        self.running = True
        self.message = ""
        self.w = threading.Thread(name='commandThread', target=self.commandThread)
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.01)
        print(self.ser.name)
        self.w.start()

    def generateMessage(self, command, params=None):
        if params is None:
            self.message = command + "\r\n"
        else:
            self.message = command + ':' + ':'.join(params) + "\r\n"

    def gs(self):
        self.ser.write('gs\r\n'.encode("utf-8"))
        response = self.ser.read(20).decode("utf-8")
        return response

    # sd:left:back:right
    def forward(self, speed):
        self.generateMessage("sd", [speed, 0, -speed])

    def reverse(self, speed):
        self.generateMessage("sd", [-speed, 0, speed])

    def left(self, speed):
        self.generateMessage("sd", [-speed, -speed, -speed])

    def right(self, speed):
        self.generateMessage("sd", [speed, speed, speed])

    def throw(self, speed):
        self.generateMessage("d", speed)

    def __del__(self):
        self.running = False
        self.speed = [0, 0, 0]
        self.ser.close()
