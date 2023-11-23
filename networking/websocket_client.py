import websockets
import asyncio
import json

class WebsocketClient():
    def __init__(self, server_addr, client_id, bot_client_inbound, ws_outbound) -> None:
        self.client_id = client_id
        self.bot_client_inbound = bot_client_inbound
        self.ws_outbound = ws_outbound
        self.server_addr = server_addr
    
    async def receive_message(self, websocket):
        try:
            while True:
                inbound_msg = await websocket.recv()
                if type(inbound_msg) is str:
                    inbound_msg = json.loads(inbound_msg)
                await self.bot_client_inbound.put(inbound_msg)
        except Exception as e:
            print(e)
            return await self.start()
    
    async def send_message(self, websocket):
        try:
            while True:
                outbound_msg = await self.ws_outbound.get()
                outbound_msg["invokedRouteKey"] = "processMessage"
                outbound_msg["client_id"] = self.client_id
                await websocket.send(json.dumps(outbound_msg))
        except Exception as e:
            print(e)
            return await self.start()

    async def start(self):
        websocket_endpoint = f"{self.server_addr}?bot={self.client_id}"
        async with websockets.connect(websocket_endpoint) as websocket:
            asyncio.create_task(self.receive_message(websocket))
            asyncio.create_task(self.send_message(websocket))
            await asyncio.Future()