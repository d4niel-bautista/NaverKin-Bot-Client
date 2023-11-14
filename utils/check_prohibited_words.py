async def has_prohibited_words(text: str, prohibited_words: list):
    if not any(prohib_word in text for prohib_word in prohibited_words):
        return False
    return True