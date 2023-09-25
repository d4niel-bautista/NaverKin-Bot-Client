import asyncio

class Service():
    def __init__(self, queues) -> None:
        self.ws_outbound = queues.ws_outbound
        self.service_outbound = queues.service_outbound
        self.service_inbound = queues.service_inbound
        self.bot_client_inbound = queues.bot_client_inbound
    
    async def process_outbound_message(self):
        while True:
            outbound_msg = await self.service_outbound.get()
            await self.ws_outbound.put(outbound_msg)
    
    async def process_inbound_message(self):
        while True:
            inbound_msg = await self.service_inbound.get()
            await self.bot_client_inbound.put(inbound_msg)