from websockets import client
from websockets.exceptions import ConnectionClosed
import asyncio
import json
from networking.service import update_state, get_connection_info, update_autoanswerbot_configs

class WebsocketClient():
    def __init__(self, server_addr, client_id, bot_client_inbound, ws_outbound, VM_id="") -> None:
        self.client_id = client_id
        self.connection_id = ""
        self.group_id = ""
        self.VM_id = VM_id
        self.bot_client_inbound = bot_client_inbound
        self.ws_outbound = ws_outbound
        self.server_addr = server_addr
        self.websocket = None
        self.reconnect_lock = asyncio.Lock()
        self.is_reconnecting = False
        self.disable_reconnection = False
        self.account = {}
        self.account_ids = []
        self.prompt_configs = {}
        self.botconfigs = {}
    
    async def connect(self):
        try:
            websocket_endpoint = f"{self.server_addr}?bot={self.client_id}&group_id={self.group_id}&VM_id={self.VM_id}"
            self.websocket = await client.connect(websocket_endpoint)
            print(f"{self.client_id.upper()} CONNECTED")
        except Exception as e:
            print(f"Connecting error: {repr(e)}")
            await asyncio.sleep(10)
            return await self.connect()
    
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
            
            print("Reconnecting...")
            self.is_reconnecting = True
            if not self.websocket.closed:
                await self.websocket.close()
            else:
                print("Websocket is already closed")
            await asyncio.sleep(5)
            await self.connect()
            await get_connection_info()
            if len(self.account) > 0:
                await update_state(state=2)
                if self.client_id == "autoanswerbot":
                    await update_autoanswerbot_configs(account=self.account, account_ids=self.account_ids, prompt_configs=self.prompt_configs, botconfigs=self.botconfigs)
            self.is_reconnecting = False
    
    async def receive_message(self):
        while True:
            try:
                if self.disable_reconnection or not self.websocket or self.websocket.closed:
                    await asyncio.sleep(1)
                    continue
                
                inbound_msg = await self.websocket.recv()
                if type(inbound_msg) is str:
                    inbound_msg = json.loads(inbound_msg)

                if "connection_info" in inbound_msg:
                    self.group_id = inbound_msg["connection_info"]["group_id"]
                    self.connection_id = inbound_msg["connection_info"]["connection_id"]
                    print(inbound_msg)
                    continue
                
                if inbound_msg["type"] == "response_data":
                    if "account_url" in inbound_msg["data"]:
                        self.account = inbound_msg["data"]
                    elif "prompt" in inbound_msg["data"]:
                        self.prompt_configs = inbound_msg["data"]
                    elif "answers_per_day" in inbound_msg["data"]:
                        self.botconfigs = inbound_msg["data"]
                    elif "account_ids" in inbound_msg["data"]:
                        inbound_msg["data"] = inbound_msg["data"]["account_ids"]
                        self.account_ids = inbound_msg["data"]

                await self.bot_client_inbound.put(inbound_msg)
            except ConnectionClosed as e:
                print(f"WebSocket connection closed during receiving: {e}")
                await self.reconnect()
            except Exception as e:
                print(f"An unexpected error occurred when receiving: {repr(e)}")
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
                outbound_msg["group_id"] = self.group_id
                outbound_msg["connection_id"] = self.connection_id
                await self.websocket.send(json.dumps(outbound_msg))
            except ConnectionClosed as e:
                print(f"WebSocket connection closed during receiving: {e}")
                await self.reconnect()
            except Exception as e:
                print(f"An unexpected error occurred during sending: {repr(e)}")
                await self.reconnect()

    async def start(self):
        await self.connect()
        receive_task = asyncio.create_task(self.receive_message())
        send_task = asyncio.create_task(self.send_message())
        await get_connection_info()
        await asyncio.gather(receive_task, send_task)