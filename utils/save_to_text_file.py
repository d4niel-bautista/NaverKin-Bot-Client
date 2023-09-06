import os

def save_to_text_file(filename, directory, content):
    if not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    if not os.path.isfile(filepath):
        with open(filepath, 'w+') as f:
            f.close()
    with open(filepath, 'w+') as f:
            f.write(content)