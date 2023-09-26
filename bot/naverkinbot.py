from .async_worker import AsyncWorker

class NaverKinBot(AsyncWorker):
    def __init__(self, queues) -> None:
        super().__init__(queues)
        self.stop = False
    
    async def execute_task(self, task: str):
        if task == "START":
            pass
        elif task == "STOP":
            self.stop = True
    
    