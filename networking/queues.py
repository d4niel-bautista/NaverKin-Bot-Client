import asyncio

ws_outbound = asyncio.Queue(maxsize=10)
bot_client_inbound = asyncio.Queue(maxsize=10)