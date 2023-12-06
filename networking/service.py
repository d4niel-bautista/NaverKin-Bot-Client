from networking.queues import ws_outbound
from datetime import datetime

async def send_notification(send_to: str, data: dict):
    outbound_msg = {}
    outbound_msg["type"] = "notification"
    outbound_msg["send_to"] = send_to
    outbound_msg["data"] = data
    await ws_outbound.put(outbound_msg)

async def send_get_request(table: str, filters: dict):
    outbound_msg = {}
    outbound_msg["type"] = "get"
    outbound_msg["table"] = table
    outbound_msg["filters"] = filters
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

async def save_answer_response(question_url: str, type: str, content: str, username: str, date_answered: datetime, postscript:str="", status: int=1):
    await save_request(table="naverkin_answer_responses", data={"question_url": question_url, "type": type, "content": content, "username": username, "postscript": postscript, "status": status, "date_answered": date_answered})

async def save_question_post(question_url: str, title: str, author: str, respondent: str, date_posted: datetime, status: int=0):
    await save_request(table="naverkin_question_posts", data={"url": question_url, "title": title, "author": author, "date_posted": date_posted, "respondent": respondent, "status": status})

async def save_login(username: str, ip_address: str, login_timestamp: datetime):
    await save_request(table="logins", data={"username": username, "ip_address": ip_address, "login_timestamp": login_timestamp})

async def update_account_interactions(question_bot_username: str, answer_bot_username: str):
    await send_update_request(table="account_interactions", data={"username": question_bot_username}, filters={"username": answer_bot_username})

async def get_answer_response(filters: dict):
    await send_get_request(table="naverkin_answer_responses", filters=filters)

async def websocket_connect():
    await ws_outbound.put("connect")

async def websocket_disconnect():
    await ws_outbound.put("disconnect")

async def update_state(state: int):
    outbound_msg = {}
    outbound_msg["type"] = "update_state"
    outbound_msg["update_state"] = state
    await ws_outbound.put(outbound_msg)

async def get_connection_info():
    outbound_msg = {}
    outbound_msg["type"] = "get_connection_info"
    await ws_outbound.put(outbound_msg)