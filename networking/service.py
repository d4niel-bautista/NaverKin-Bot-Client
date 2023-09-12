from networking.client import Client
import networking.messages as msg
from utils import save_to_text_file

class Service():
    client = None

    def __init__(self, client: Client):
        self.client = client
    
    def get_account(self):
        request = msg.GET_ID
        self.client.send(request)
        response = self.client.receive()
        return response

    def get_account_interactions(self, username):
        request = msg.GET_ACCOUNT_INTERACTIONS
        request['data']['username'] = username
        self.client.send(request)
        response = self.client.receive()
        return response
    
    def get_configs(self, role: int):
        request = msg.GET_CONFIGS
        request['data']['config_id'] = role
        self.client.send(request)
        response = self.client.receive()
        if type(response) is dict:
            save_to_text_file('prescript.txt', 'configs', response.pop('prescript'))
            save_to_text_file('prompt.txt', 'configs', response.pop('prompt'))
            save_to_text_file('postscript.txt', 'configs', response.pop('postscript'))
            save_to_text_file('openai_api_key.txt', 'configs', response.pop('openai_api_key'))
        return response
    
    def get_question(self, username, role, levelup_id):
        if role == 0:
            request = msg.GET_QUESTION
            request['data']['levelup_id'] = levelup_id
            request['data']['username'] = username
        elif role == 1:
            request = msg.SELECT_QUESTION
            request['data']['username'] = username + "::author"
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
    
    def update_question(self, question_id, respondent='', author='', status=0):
        request = msg.UPDATE_QUESTION
        request['data']['id'] = question_id
        request['data']['respondent'] = respondent
        request['data']['author'] = author
        request['data']['status'] = status
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
    
    def save_question(self, id, title, username):
        request = msg.SAVE_QUESTION
        request['data']['question_id'] = id
        request['data']['question_title'] = title
        request['data']['author'] = username
        self.client.send(request)
        response = self.client.receive()
        return response