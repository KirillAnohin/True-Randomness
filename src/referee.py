from threading import Thread
import json
from src import config


class Referee:

    def listen(self):
        while True:
            message = self.ws.recv()
            if message != "":
                command = json.loads(message)

                if command["signal"] == "stop" and self.robot in command["targets"]:
                    self.go = False
                elif command["signal"] == "start" and self.robot in command["targets"]:
                    index = command["targets"].index(self.robot)
                    color = command["baskets"][index]
                    self.basketColor = color
                    self.go = True
                else:
                    pass

    def __init__(self, ws):
        # Params
        self.parser = config.config()
        self.go = False
        self.stopped = False
        self.robotID = self.parser.get("Game", "robotID")
        self.basketColor = ""
        # Server address
        self.ws = ws
        # Start Thread
        self.w = Thread(name='refereeThread', target=self.listen)
        self.w.start()

    def stop(self):
        self.stopped = True
