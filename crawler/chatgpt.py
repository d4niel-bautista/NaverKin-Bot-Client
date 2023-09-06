import openai

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
    return response_message