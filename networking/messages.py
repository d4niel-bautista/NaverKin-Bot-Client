DISCONNECT = {'message': 'DISCONNECT'}
GET_ID = {'message': 'GET_ACCOUNT'}
GET_ACCOUNT_INTERACTIONS = {'message': 'GET_ACCOUNT_INTERACTIONS', 'data': {'username': ''}}
GET_CONFIGS = {'message': 'GET_CONFIGS', 'data': {'config_id': ''}}
GET_QUESTION = {'message': 'GET_QUESTION', 'data': {'username': '', 'levelup_id': ''}}
SELECT_QUESTION = {'message': 'SELECT_QUESTION', 'data': {'username': ''}}
GET_COOKIES = {'message': 'GET_COOKIES', 'data': {'username': ''}}
SAVE_COOKIES = {'message': 'SAVE_COOKIES', 'data': {'username': '', 'cookies': []}}
SAVE_QUESTION = {'message': 'SAVE_QUESTION', 'data': {'question_id': '', 'question_title': '', 'author': ''}}
GET_USERAGENT = {'message': 'GET_USERAGENT', 'data': {'username': ''}}
SAVE_USERAGENT = {'message': 'SAVE_USERAGENT', 'data': {'username': '', 'useragent': ''}}
UPDATE_ACCOUNT = {'message': 'UPDATE_ACCOUNT', 'data': {'username': '', 'status': ''}}
UPDATE_QUESTION = {'message': 'UPDATE_QUESTION', 'data': {'id': '', 'respondent': '', 'author': '', 'status': ''}}
ID_REACHED_LIMIT = {'message': 'ID_REACHED_LIMIT'}