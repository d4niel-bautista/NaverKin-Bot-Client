from .async_worker import AsyncWorker

class NaverKinBot(AsyncWorker):
    def __init__(self, queues) -> None:
        super().__init__(queues)
        self.prev_account = ''
        self.stop = False
        self.on_error = False
    
    async def execute_task(self, task: str):
        if task == "START":
            pass
        elif task == "STOP":
            self.stop = True
    
    async def get(self, table: str, column: str = "*", params: dict = {}):
        table = table.replace(" ", "")
        table = table.split(",")
        column = column.replace(" ", "")
        column = column.split(",")
        await self.service_outbound.put({"query": "get", "data": {"table": table, "column": column, "params": params}})
    
    async def insert(self, table: str, column: str, values: str, params: dict = {}):
        column = column.replace(" ", "")
        column = column.split(",")
        values = values.replace(" ", "")
        values = values.split(",")
        await self.service_outbound.put({"query": "insert", "data": {"table": table, "column": column, "values": values, "params": params}})
    
    async def update(self, table: str, column: dict, params: dict = {}):
        await self.service_outbound.put({"query": "update", "data": {"table": table, "column": column, "params": params}})
    