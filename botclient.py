from networking.client import Client
from networking.service import Service
from crawler.crawler import Crawler

client = Client()
service = Service(client)
crawler = Crawler(service)
crawler.start()