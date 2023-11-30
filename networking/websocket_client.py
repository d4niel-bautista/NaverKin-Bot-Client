import websockets
import websockets.exceptions
import asyncio
import json

class WebsocketClient():
    def __init__(self, server_addr, client_id, bot_client_inbound, ws_outbound) -> None:
        self.client_id = client_id
        self.bot_client_inbound = bot_client_inbound
        self.ws_outbound = ws_outbound
        self.server_addr = server_addr
        self.websocket = None
        self.reconnect_lock = asyncio.Lock()
        self.is_reconnecting = False
        self.disable_reconnection = False
    
    async def connect(self):
        websocket_endpoint = f"{self.server_addr}?bot={self.client_id}"
        self.websocket = await websockets.connect(websocket_endpoint)
    
    async def reconnect(self):
        if self.is_reconnecting:
            return
        elif self.disable_reconnection:
            print("Reconnection currently disabled")
            await asyncio.sleep(1)
            return
        
        async with self.reconnect_lock:
            if self.is_reconnecting:
                return
            elif self.disable_reconnection:
                print("Reconnection currently disabled")
                await asyncio.sleep(1)
                return

            self.is_reconnecting = True
            try:
                await self.websocket.close()
                await self.connect()
            finally:
                self.is_reconnecting = False
    
    async def receive_message(self):
        while True:
            try:
                if self.disable_reconnection:
                    await asyncio.sleep(1)
                    continue
                
                inbound_msg = await self.websocket.recv()
                if type(inbound_msg) is str:
                    inbound_msg = json.loads(inbound_msg)
                await self.bot_client_inbound.put(inbound_msg)
            except websockets.exceptions.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
                await self.reconnect()
            except Exception as e:
                print(f"An unexpected error occurred when receiving: {e}")
                await self.reconnect()

    async def send_message(self):
        while True:
            try:
                outbound_msg = await self.ws_outbound.get()
                if outbound_msg == "disconnect":
                    print("WebSocket disabled")
                    self.disable_reconnection = True
                    await self.websocket.close()
                    continue
                elif outbound_msg == "connect":
                    print("WebSocket enabled")
                    self.disable_reconnection = False
                    await self.reconnect()
                    continue

                outbound_msg["action"] = "processMessage"
                outbound_msg["client_id"] = self.client_id
                await self.websocket.send(json.dumps(outbound_msg))
            except websockets.exceptions.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
                await self.reconnect()
            except Exception as e:
                print(f"An unexpected error occurred during sending: {e}")
                await self.reconnect()

    async def start(self):
        await self.connect()
        receive_task = asyncio.create_task(self.receive_message())
        send_task = asyncio.create_task(self.send_message())
        await asyncio.gather(receive_task, send_task)