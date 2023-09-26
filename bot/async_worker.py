import asyncio

class AsyncWorker():
    def __init__(self, queues) -> None:
        self.bot_client_inbound = queues.bot_client_inbound
        self.service_outbound = queues.service_outbound
        self.data_queue = asyncio.Queue(maxsize=1)
    
    async def process_inbound_message(self):
        while True:
            inbound_msg = await self.bot_client_inbound.get()
            if inbound_msg["type"] == "response_data":
                await self.data_queue.put(inbound_msg["data"])
            elif inbound_msg["type"] == "task":
                await self.execute_task(inbound_msg["message"])
    
    async def execute_task(self, task: str):
        pass
    
    async def start(self):
        asyncio.create_task(self.process_inbound_message())
        await asyncio.Future()

