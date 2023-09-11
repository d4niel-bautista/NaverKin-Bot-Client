import re

def clean_question_content(tag):
    [i.decompose() for i in tag.find_all('span', {'class' : 'blind'})]
    [i.decompose() for i in tag.find_all('span', {'class' : 'grade-point'})]
    question_content_cleaned = re.sub('\t+', '', tag.text)
    question_content_cleaned = re.sub('\n{1,}', '\n', question_content_cleaned)
    question_content_cleaned = question_content_cleaned.strip()
    return question_content_cleaned