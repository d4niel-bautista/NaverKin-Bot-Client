from bot import NaverKinBot

class AnswerBot(NaverKinBot):
    def __init__(self, queues, mode) -> None:
        super().__init__(queues)
        self.mode = mode