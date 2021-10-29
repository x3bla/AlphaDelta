import videoqueue

class AutoPlay:
    """make a flag, while flag: autoplay; else return"""

    def __init__(self, server):
        self.loop = False
        self.auto_play_flag = False
        self.server = server
        self.queue = videoqueue.VideoQueue().displayQueue(server)

    def play(self):
        raise NotImplementedError

    async def skip(self):
        raise NotImplementedError

class DiscordMusicBot:

    def __init__(self, server):
        self.queue = videoqueue.VideoQueue()
        self.autoplay = AutoPlay(server)
        self.server = server


