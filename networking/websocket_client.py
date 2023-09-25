import websockets
import asyncio

class WebsocketClient():
    def __init__(self, client_id, queues) -> None:
        self.client_id = client_id
        self.service_inbound = queues.service_inbound
        self.ws_outbound = queues.ws_outbound
    
    async def receive_message(self, websocket):
        while True:
            inbound_msg = await websocket.recv()
            await self.service_inbound.put(inbound_msg)
    
    async def send_message(self, websocket):
        while True:
            outbound_msg = await self.ws_outbound.get()
            await websocket.send_json(outbound_msg)

    async def start(self):
        async with websockets.connect(f"ws://localhost:8000/{self.client_id}") as websocket:
            asyncio.create_task(self.receive_message(websocket))
            asyncio.create_task(self.send_message(websocket))
            await asyncio.Future()