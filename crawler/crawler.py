from networking.service import Service

class Crawler():
    username = ''
    password = ''
    submit_delay = 60
    page_refresh = 300
    on_error = False
    stop = False
    service = None

    def __init__(self, service: Service):
        self.service = service
    
    def get_account(self):
        response = self.service.get_account()
        if type(response) is dict:
            self.username = response['username']
            self.password = response['password']
            print(self.username)

    def get_question(self):
        question = self.service.get_question(self.username)
        print(question['id'], question)
