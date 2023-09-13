from networking.client import Client
from networking.service import Service
from bot.questionbot import QuestionBot
from bot.answerbot import AnswerBot
import argparse

def start():
    client = Client()
    service = Service(client)

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-bt", help="Sets which bot type to use.\nInput 'a' for AnswerBot or 'q' for QuestionBot.", required=True, choices=['a', 'q'])
    args = parser.parse_args()
    if args.bt == 'a':
        bot = AnswerBot(service)
        print('STARTING ANSWERBOT')
    elif args.bt == 'q':
        bot = QuestionBot(service)
        print('STARTING QUESTIONBOT')
    bot.start()

if __name__ == '__main__':
    start()