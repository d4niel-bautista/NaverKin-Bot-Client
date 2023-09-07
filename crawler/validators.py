import re

def text_has_prohibited_words(prohibited_words: list, text: str) -> bool:
    if prohibited_words:
        for word in prohibited_words:
            if word.strip() in text:
                return True
    return False

def text_has_links(text: str) -> bool:
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>???¡°¡±¡®¡¯]))"
    if re.search(regex, text):
        return True
    return False

def text_has_korean_characters(text: str) -> bool:
    korean_pattern = re.compile("[\uac00-\ud7af]+")
    result = korean_pattern.search(text)
    return bool(result)