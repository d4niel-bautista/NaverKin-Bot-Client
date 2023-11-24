from networking.queues import ws_outbound
from datetime import datetime

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

async def send_logging_data(level: str, log: str):
    outbound_msg = {}
    outbound_msg["type"] = "logging"
    outbound_msg["level"] = level
    outbound_msg["log"] = log
    await ws_outbound.put(outbound_msg)

async def save_request(table: str, data: dict):
    outbound_msg = {}
    outbound_msg["type"] = "save"
    outbound_msg["table"] = table
    outbound_msg["data"] = data
    await ws_outbound.put(outbound_msg)

async def save_answer_response(question_url: str, type: str, content: str, username: str, postscript:str="", status: int=1, date_answered: datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    await save_request(table="naverkin_answer_responses", data={"question_url": question_url, "type": type, "content": content, "username": username, "postscript": postscript, "status": status, "date_answered": date_answered})

async def update_account_interactions(question_bot_username: str, answer_bot_username: str):
    await send_update_request(table="account_interactions", data={"username": question_bot_username}, filters={"username": answer_bot_username})