from .async_worker import AsyncWorker
import asyncio

class NaverKinBot(AsyncWorker):
    def __init__(self, queues) -> None:
        super().__init__(queues)
        self.account = {}
        self.user_session = {}
        self.configs = {}
        self.prev_account = ''
        self.running = False
        self.stop = False
        self.on_error = False
    
    async def execute_task(self, task: str):
        if task == "START":
            if not self.running:
                self.running = True
                asyncio.create_task(self.main())
        elif task == "STOP":
            self.stop = True
    
    async def main(self):
        print("STARTED")

        # WAIT FOR SERVER TO SEND USERNAME/PASSWORD
        self.account = await self.data_queue.get()
        print(f"{self.account['username']} LOGGED IN")

        #WAIT FOR SERVER TO SEND USER SESSION
        self.user_session = await self.data_queue.get()

        #WAIT FOR SERVER TO SEND CONFIGS
        self.configs = await self.data_queue.get()
        print("END")
        return
    