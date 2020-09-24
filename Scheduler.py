import schedule
from datetime import datetime
import time

# 相關設定
IPCMDLocation                                                       = "./IPMsg/x64/Release/ipcmd.exe"
IPMsgLocation                                                       = "./IPMsg/x64/Release/IPMsg.exe"
PodcastMessage                                                      = "請大家在 18:30 分填完進度 by Duke"
IsLastPodcast                                                       = False                                 # 時間到了結束這個廣播
#PodcastTiming                                                       = ["17:30", "18:00", "18:30"]           # 廣播時間
PodcastTiming                                                       = [":00", ":10", ":30"]                 # 廣播時間


# 傳送相關的人物設定

#
def StartPodcastJob():
    DoPodcastJob(False)
    schedule.clear()

    for i in range(1, len(PodcastTiming)):
        if i == len(PodcastTiming) - 1:
            schedule.every().minute.at(PodcastTiming[i]).do(DoPodcastJob, True)
        else:
            schedule.every().minute.at(PodcastTiming[i]).do(DoPodcastJob)
    print(schedule.next_run())


def DoPodcastJob(LastCheck = False):
    # 結束之後要中斷
    global IsLastPodcast
    IsLastPodcast = LastCheck

    # 每隔一段時間會重複
    Now = datetime.now()
    print(Now.strftime("%Y-%m-%d %H:%M:%S.%f")[0: -3] + " => Send all messages")

#schedule.every().day.at(PodcastTiming[0]).do(StartPodcastJob)
schedule.every().minute.at(PodcastTiming[0]).do(StartPodcastJob)
while not IsLastPodcast:
    schedule.run_pending()
    time.sleep(1)