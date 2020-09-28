import schedule
from datetime import datetime
import time
import subprocess
import json

# 相關設定
IPCMDLocation                                                       = "./Tools/ipcmd.exe"
IPMsgLocation                                                       = "./Tools/IPMsg.exe"
PodcastMessage                                                      = "請大家在18:30分前填完進度\n如果填過請忽略\n\nby　Duke廣播器(v2)"                          # 時間到了結束這個廣播
PodcastMessageUrgent                                                = "快填啦!!\n\nby　Duke廣播器(v2)"         # 時間到了結束這個廣播
# PodcastTiming                                                       = ["17:30", "17:40", "17:50", "18:00", "18:10", "18:20", "18:29"]           # 廣播時間
PodcastTiming                                                       = [":00", ":10", ":30"]                 # 廣播時間
# SettingLocation                                                     = "./Setting.json"                      # 放資料的地方 (由於安全性的考量，所以請自行填寫)
SettingLocation                                                     = "./SettingTest.json"

####################################################################
# Helper Function
####################################################################
# 讀取設定檔的 Json
def ReadSettingJSON():
    f = open(SettingLocation, 'r', encoding="utf-8")
    data = json.load(f)
    f.close()
    return data
# 拿取資料的 List
def GetCMDList():
    process = subprocess.Popen([IPCMDLocation, "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = process.communicate()
    return stdout.decode("utf-8").split("\r\n")[:-2]
def SplitResult(info):
    data    = info.split("/")
    PCName  = data[-1][:-1]
    IP      = data[-2]
    return PCName, IP

#
def DoPodcastJob(IsFinal = False):
    global UserData

    # 每隔一段時間會重複
    Now = datetime.now()
    print(Now.strftime("%Y-%m-%d %H:%M:%S.%f")[0: -3] + " => Send all messages")

    # 抓取所有人的 IP Info
    # 去判斷哪些要送
    IPInfo = GetCMDList()
    for ipinfo in IPInfo:
        pcname, ip = SplitResult(ipinfo)
        for user in UserData:
            index = pcname.find(user["PCName"])
            if (index >= 0):
                # print(pcname + " " + ip)
                process = subprocess.Popen([IPMsgLocation, "/MSG", ip, PodcastMessage], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _, _ = process.communicate()
                # print(stdout, stderr)


# Main
UserData = ReadSettingJSON()
for podcasttime in PodcastTiming:
    # schedule.every().day.at(time).do(DoPodcastJob)
    schedule.every().minute.at(podcasttime).do(DoPodcastJob)
print("Start Podcast!!")
while True:
    schedule.run_pending()
    time.sleep(1)