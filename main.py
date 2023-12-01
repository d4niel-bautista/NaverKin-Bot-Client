from bot import AnswerBot, AutoanswerBot, QuestionBot
from networking.queues import ws_outbound, bot_client_inbound
from networking.websocket_client import WebsocketClient
import argparse
import asyncio

async def start():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-bt", help="Sets which bot type to use.\nInput 'aa' for AnswerBot_Advertisement, 'ae' for AnswerBot_Exposure, or 'q' for QuestionBot.", required=True, choices=['aa', 'ae', 'au', 'q'])
    parser.add_argument("-s", help="Sets the server address.", required=True)
    args = parser.parse_args()
    server = args.s
    if args.bt == 'aa':
        bot = AnswerBot(bot_client_inbound, mode=0)
        client_id = "answerbot_advertisement"
    elif args.bt == 'ae':
        bot = AnswerBot(bot_client_inbound, mode=1)
        client_id = "answerbot_exposure"
    elif args.bt == 'au':
        bot = AutoanswerBot(bot_client_inbound)
        client_id = "autoanswerbot"
    elif args.bt == 'q':
        bot = QuestionBot(bot_client_inbound)
        client_id = "questionbot"
    ws_client = WebsocketClient(server, client_id, bot_client_inbound, ws_outbound)
    await asyncio.gather(bot.start(), ws_client.start())

asyncio.run(start())