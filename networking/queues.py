import asyncio

class QueuesContainer():
    def __init__(self) -> None:
        self.ws_outbound = asyncio.Queue(maxsize=1)
        self.service_outbound = asyncio.Queue(maxsize=1)
        self.service_inbound = asyncio.Queue(maxsize=1)
        self.bot_client_inbound = asyncio.Queue(maxsize=1)