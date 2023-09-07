from googletrans import Translator

def translate_to_korean(text):
    translator = Translator(service_urls=['translate.googleapis.com'])
    detected_language = translator.detect(text).lang
    translation = translator.translate(text, src=detected_language, dest='ko')
    return translation.text
