import os

def save_to_text_file(filename, directory, content: str):
    if not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    if not os.path.isfile(filepath):
        with open(filepath, 'wb+') as f:
            f.close()
    with open(filepath, 'wb+') as f:
            f.write(content.rstrip().encode('euc-kr'))