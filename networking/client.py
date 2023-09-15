import socket
import networking.messages as msg
import os
import json
from utils import fetch_server_ip
from dotenv import load_dotenv
load_dotenv()
import threading

PORT = int(os.getenv('SERVER_PORT'))
CODEC = os.getenv('CODEC')
HEADER_LEN = int(os.getenv('HEADER_LEN'))
SERVER_IP = fetch_server_ip()

class Client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self):
        self.connect()
        # self.receive_thread = threading.Thread(target=self.receive_push_message, daemon=True)
        # self.receive_thread.start()

    def set_service(self, service):
        self.service = service

    def connect(self):
        self.client.connect((SERVER_IP, PORT))

    def disconnect(self):
        self.send(msg.DISCONNECT)
        response = self.receive()
        return response

    def send(self, message: str):
        message = json.dumps(message)
        self.client.send(message.encode(CODEC))
    
    def receive(self):
        message = self.client.recv(HEADER_LEN).decode(CODEC)
        message = json.loads(message)
        if type(message) is dict:
            if 'notif' in message.keys():
                return
        return message
    
    def receive_push_message(self):
        message = self.client.recv(HEADER_LEN).decode(CODEC)
        message = json.loads(message)
        if type(message) is dict:
            if 'notif' in message.keys():
                self.service.handle_push_messages(message)