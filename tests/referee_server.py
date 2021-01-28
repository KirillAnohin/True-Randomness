import asyncio
import websockets
import json


@asyncio.coroutine
async def server(websocket, uri):
    while True:
        cmd = int(input("vali käsk"))
        if cmd == 1:
            name = {
                "signal": "start",
                "targets": ["Io", "TR"],
                "baskets": ["magenta", "magenta"]
            }
        elif cmd == 2:
            name = {
                "signal": "stop",
                "targets": ["Io", "TR"],
            }
        elif cmd == 3:
            name = {
                "signal": "start",
                "targets": ["Io", "TR"],
                "baskets": ["magenta", "blue"]
            }
        y = json.dumps(name)

        await websocket.send(y)


# Below line has the SERVER IP address, not client.
start_server = websockets.serve(server, '192.168.3.26', 9090)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
