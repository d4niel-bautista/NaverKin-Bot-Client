import asyncio

ws_outbound = asyncio.Queue(maxsize=1)
bot_client_inbound = asyncio.Queue(maxsize=1)