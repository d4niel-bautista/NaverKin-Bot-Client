from networking.client import Client
import networking.messages as msg

class Service():
    client = None

    def __init__(self, client: Client):
        self.client = client
    
    def get_account(self):
        request = msg.GET_ID
        self.client.send(request)
        response = self.client.receive()
        return response
    
    def get_question(self, username):
        request = msg.GET_QUESTION
        request['data']['username'] = username
        self.client.send(request)
        response = self.client.receive()
        return response
    
    def disconnect(self):
        self.client.disconnect()