from bot import AnswerBot, QuestionBot
from networking.queues import QueuesContainer
from networking.service import Service
from networking.websocket_client import WebsocketClient
import argparse
import asyncio

queues = QueuesContainer()
service = Service(queues)

async def start():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-bt", help="Sets which bot type to use.\nInput 'aa' for AnswerBot_Advertisement, 'ae' for AnswerBot_Exposure, or 'q' for QuestionBot.", required=True, choices=['aa', 'ae', 'q'])
    args = parser.parse_args()
    if args.bt == 'aa':
        bot = AnswerBot(queues=queues, mode=0)
        ws_client = WebsocketClient("AnswerBot_Advertisement", queues)
        print('STARTING ANSWERBOT_ADVERTISEMENT')
    elif args.bt == 'ae':
        bot = AnswerBot(queues=queues, mode=1)
        ws_client = WebsocketClient("AnswerBot_Exposure", queues)
        print('STARTING ANSWERBOT_EXPOSURE')
    elif args.bt == 'q':
        bot = QuestionBot(queues=queues)
        ws_client = WebsocketClient("QuestionBot", queues)
        print('STARTING QUESTIONBOT')
    await asyncio.gather(bot.start(), service.start(), ws_client.start())

asyncio.run(start())