from networking.client import Client
from networking.service import Service
from bot.questionbot import QuestionBot
from bot.answerbot import AnswerBot

client = Client()
service = Service(client)
bot = AnswerBot(service)
bot.start()