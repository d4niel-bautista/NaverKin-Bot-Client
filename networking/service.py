from networking.queues import ws_outbound

async def send_notification(send_to: str, data: dict):
    outbound_msg = {}
    outbound_msg["type"] = "notification"
    outbound_msg["send_to"] = send_to
    outbound_msg["data"] = data
    await ws_outbound.put(outbound_msg)

async def send_update_request(table: str, data: dict, filters: dict):
    outbound_msg = {}
    outbound_msg["type"] = "update"
    outbound_msg["table"] = table
    outbound_msg["data"] = data
    outbound_msg["filters"] = filters
    await ws_outbound.put(outbound_msg)