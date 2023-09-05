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
    
    def get_cookies(self, username):
        request = msg.GET_COOKIES
        request['data']['username'] = username
        self.client.send(request)
        response = self.client.receive()
        return response
    
    def save_cookies(self, username, cookies):
        request = msg.SAVE_COOKIES
        request['data']['username'] = username
        request['data']['cookies'] = cookies
        self.client.send(request)
        response = self.client.receive()
        return response
    
    def get_useragent(self, username):
        request = msg.GET_USERAGENT
        request['data']['username'] = username
        self.client.send(request)
        response = self.client.receive()
        return response
    
    def save_useragent(self, username, useragent):
        request = msg.SAVE_USERAGENT
        request['data']['username'] = username
        request['data']['useragent'] = useragent
        self.client.send(request)
        response = self.client.receive()
        return response
    
    def update_question(self, question_id, username):
        request = msg.UPDATE_QUESTION
        request['data']['id'] = question_id
        request['data']['respondent'] = username
        self.client.send(request)
        response = self.client.receive()
        return response
    
    def update_account(self, username, status):
        request = msg.UPDATE_ACCOUNT
        request['data']['username'] = username
        request['data']['status'] = status
        self.client.send(request)
        response = self.client.receive()
        return response
    
    def disconnect(self, username):
        request = msg.UPDATE_ACCOUNT
        request['data']['username'] = username
        request['data']['status'] = 0
        self.client.send(request)
        response = self.client.receive()
        self.client.disconnect()
        return response