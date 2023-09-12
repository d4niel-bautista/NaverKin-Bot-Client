import openai
import json
import time
from .validators import text_has_korean_characters
from utils import translate_to_korean

def set_api_key():
    with open('configs/openai_api_key.txt', 'r+') as f:
        api_key = f.read().rstrip()
        if api_key:
            openai.api_key = api_key

def get_prompt():
    with open('configs/prompt.txt', 'rb+') as f:
        prompt = f.read().decode('euc-kr').rstrip()
    return prompt

def generate_response(query):
    prompt = get_prompt()
    set_api_key()
    messages = [{"role": "system", "content": prompt},
                {"role": "user", "content": query}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    response_message = response["choices"][0]["message"].content
    if not query == '한국어를 사용하여 구체적인 질문을 하고 제목과 내용을 키로 하여 JSON 형식으로 응답합니다.':
        if not text_has_korean_characters(response_message):
            response_message = translate_to_korean(response_message)
    return response_message

def generate_question(query='한국어를 사용하여 구체적인 질문을 하고 제목과 내용을 키로 하여 JSON 형식으로 응답합니다.'):
    while True:
        question = generate_response(query)
        try:
            question = json.loads(question)
            if type(question) is dict:
                if question.get('title') and question.get('content'):
                    title = question.pop('title')
                    content = question.pop('content')
                    if not text_has_korean_characters(title):
                        title = translate_to_korean(title)
                    if not text_has_korean_characters(content):
                        content = translate_to_korean(content)
                    return title, content
                elif question.get('제목') and question.get('내용'):
                    title = question.pop('제목')
                    content = question.pop('내용')
                    return title, content
        except:
            pass
        time.sleep(10)