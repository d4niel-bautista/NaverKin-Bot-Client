import websockets
import asyncio
import json

class WebsocketClient():
    def __init__(self, client_id, queues) -> None:
        self.client_id = client_id
        self.service_inbound = queues.service_inbound
        self.ws_outbound = queues.ws_outbound
    
    async def receive_message(self, websocket):
        try:
            while True:
                inbound_msg = await websocket.recv()
                if type(inbound_msg) is str:
                    inbound_msg = json.loads(inbound_msg)
                await self.service_inbound.put(inbound_msg)
        except:
            return await self.start()
    
    async def send_message(self, websocket):
        try:
            while True:
                outbound_msg = await self.ws_outbound.get()
                await websocket.send(json.dumps(outbound_msg))
        except:
            return await self.start()

    async def start(self):
        async with websockets.connect(f"ws://localhost:8000/{self.client_id}") as websocket:
            asyncio.create_task(self.receive_message(websocket))
            asyncio.create_task(self.send_message(websocket))
            await asyncio.Future()