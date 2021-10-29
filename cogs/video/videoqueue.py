import downloader as ytdl
import videodata

class VideoQueueItem:  # download the video
    def __init__(self, videoData: videodata.VideoData):
        self.videoData = videoData

    async def __download(self):
        parseToList = [self.videoData.url]  # convert to ["song_name"]
        ytdl.ytdl.download(parseToList)  # they use a for loop, so the string breaks down into chars, どうしてわからない

    async def download(self):
        await self.__download()


class VideoQueue:  # a queue for each server
    """the main queue to add and extract data from a dictionary"""

    bot = {}  # set class as dictionary

    def __init__(self):
        self.queue = []

    # def displayQueue(self, server):
    #     return self.bot[server]

    def addVideo(self, server, videoTitle):
        if server not in self.bot:  # if the key "server's name" does not exist, create it.
            self.bot[server] = [False, False, videoTitle]  # Loop, auto_play_flag, songs
        else:
            self.bot[server].append(videoTitle)
        print(self.bot, "\n")

    async def removeVideo(self, server, videoItem: int):
        del (self.bot[server][videoItem])
