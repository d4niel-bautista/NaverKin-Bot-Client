import socket
import networking.messages as msg
import os
import json
from dotenv import load_dotenv
load_dotenv()

PORT = int(os.getenv('SERVER_PORT'))
CODEC = os.getenv('CODEC')
HEADER_LEN = int(os.getenv('HEADER_LEN'))
SERVER_IP = os.getenv('SERVER_IP')

class Client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self):
        self.connect()

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
        return message
