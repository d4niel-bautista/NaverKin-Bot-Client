from bot import AnswerBot, QuestionBot
from networking.queues import ws_outbound, bot_client_inbound
from networking.websocket_client import WebsocketClient
import argparse
import asyncio

async def start():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-bt", help="Sets which bot type to use.\nInput 'aa' for AnswerBot_Advertisement, 'ae' for AnswerBot_Exposure, or 'q' for QuestionBot.", required=True, choices=['aa', 'ae', 'q'])
    parser.add_argument("-s", help="Sets the server address.", required=True)
    args = parser.parse_args()
    server = args.s
    if args.bt == 'aa':
        bot = AnswerBot(bot_client_inbound, mode=0)
        ws_client = WebsocketClient(server, "AnswerBot_Advertisement", bot_client_inbound, ws_outbound)
        print('STARTING ANSWERBOT_ADVERTISEMENT')
    elif args.bt == 'ae':
        bot = AnswerBot(bot_client_inbound, mode=1)
        ws_client = WebsocketClient(server, "AnswerBot_Exposure", bot_client_inbound, ws_outbound)
        print('STARTING ANSWERBOT_EXPOSURE')
    elif args.bt == 'q':
        bot = QuestionBot(bot_client_inbound)
        ws_client = WebsocketClient(server, "QuestionBot", bot_client_inbound, ws_outbound)
        print('STARTING QUESTIONBOT')
    await asyncio.gather(bot.start(), ws_client.start())

asyncio.run(start())