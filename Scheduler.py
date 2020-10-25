import schedule
from datetime import datetime
import time
import subprocess
import json
import pandas as pd
import os

# 相關設定
IPCMDLocation                                                       = "./Tools/ipcmd.exe"
IPMsgLocation                                                       = "./Tools/IPMsg.exe"
PodcastMessages                                                     = ["=====　更新成V2了　=====",
                                                                        "請在18:30分前填完進度",
                                                                        "看到這則訊息代表你還沒填(已不會吵以填過的人)",
                                                                        "",
                                                                        "by　Duke廣播器(v2)"]                 # 時間到了結束這個廣播
PodcastMessageUrgent                                                = ["再不填今天進度就幫你填在睡覺!!　(╯°□°）╯︵┴─────┴",
                                                                        "",
                                                                        "by　Duke廣播器(v2)"]                 # 時間到了結束這個廣播
PodcastTiming                                                       = ["17:30",  "18:00", "18:29"]           # 廣播時間
# SettingLocation                                                     = "./Setting.json"                      # 放資料的地方 (由於安全性的考量，所以請自行填寫)
# ExcelLocation                                                       = ""                                    # Excel 位置


# Test 相關
ExcelLocation                                                       = "./Excels/Example.xlsx"               # Execl 位置
SettingLocation                                                     = "./SettingTest.json"                  # 放資料的地方 (由於安全性的考量，所以請自行填寫)
PodcastTiming                                                       = [":00", ":10", ":20", ":30", ":40", ":50"]    # 廣播時間

####################################################################
# Helper Function
####################################################################
# 讀取設定檔的 Jsone
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
# 找出所有在 UserData 裡面，這個 NickName 是否已填過
def FindDataInExcelList(UserData, nickname):
    for user in UserData:
        if user["Name"] == nickname:
            return user["IsFilled"]
    return False
# 將一個 Array 的填成一段話發送
def TransferToSentence(StringArray):
    TotalMsg = ""
    for msg in StringArray:
        TotalMsg += msg + "\n"
    return TotalMsg

####################################################################
# 廣播
####################################################################
def DoPodcastJob(IsLast = False):
    # 每隔一段時間會重複
    Now = datetime.now()
    print(Now.strftime("%Y-%m-%d %H:%M:%S.%f")[0: -3] + " => Send all messages")

    # 判斷變數是否存在
    if not("UserData" in globals()):
        print("抓不到 UserData 區域變數")
        return

    # 抓 Excel 的資訊
    ExcelUserDataList, IsAvailable = ReadTodayExcel()
    if not IsAvailable:                                 # 如果檔案不存在，就傳這個出去
        print(Now.strftime("%Y-%m-%d %H:%M:%S.%f")[0: -3] + " => Maybe Today don't need to fill report")
        return

    # 抓取所有人的 IP Info
    # 去判斷哪些要送
    IPInfo = GetCMDList()
    for ipinfo in IPInfo:
        pcname, ip = SplitResult(ipinfo)
        for user in UserData:
            # 找名稱裡面是否有符合的名字區段
            index = pcname.find(user["PCName"])
            if (index >= 0):
                IsFilled = FindDataInExcelList(ExcelUserDataList, user["NickName"])

                # 如果還沒填進度，所以就要開始教你填進度
                if not IsFilled:
                    print("Send => " + pcname + " " + ip)

                    # 如果是最後一個填，要吵死他
                    if not IsLast:
                        process = subprocess.Popen([IPMsgLocation, "/MSG", ip, TransferToSentence(PodcastMessages)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        _, _ = process.communicate()
                    else:
                        # 好像有一個限制不能重複傳好多筆
                        # 所以要 sleep 一秒
                        for _ in range(10):
                            process = subprocess.Popen([IPMsgLocation, "/MSG", ip, TransferToSentence(PodcastMessageUrgent)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            _, _ = process.communicate()
                            time.sleep(1)
                            # print(stdout, stderr)

####################################################################
# 檢查 Excel 有哪些人沒有填
# 會丟出一個 Boolean Array 根據這個 Array 來做判斷是否要連發訊息
####################################################################
def ReadTodayExcel():
    # 路徑名稱
    # Now = datetime.now()
    # ExcelLocation = ExcelLocation + Now.strftime("%Y-%m/%Y-%m-%d") + "/DEV20_workreport.xlsx"

    # 先確定檔案在不在
    if os.path.isfile(ExcelLocation):
        return null, False

    # 讀取 Excel 路徑
    xl = pd.ExcelFile(ExcelLocation)
    df = xl.parse(xl.sheet_names[0])        # df 代表 DataFrame
    rows, _ = df.shape

    ExcelUserDataList = []
    for i in range(3,rows):
        Data        = df.iloc[i + 0, [2, 4]]
        NextData    = None
        if (i < rows - 1):
            NextData = df.iloc[i + 1, [2, 4]]

        # 找此 Column 與 下一個 Column 是不是
        if not pd.isnull(Data[0]):
            # 先確定是不是 UserData 上面的名字
            CurrentUserData = {}
            CurrentUserData["Name"] = Data[0]

            # NextData 是空的代表不用判斷下面一個
            if NextData is None:
                if pd.isnull(Data[1]):
                    CurrentUserData["IsFilled"] = False
                else:
                    CurrentUserData["IsFilled"] = True
                ExcelUserDataList.append(CurrentUserData)
                break
            
            # 正常情況要判斷兩個
            # 1. 下一格是共同儲存格，所以要判斷此格與下一個是否都是 null
            # 2. 下一格不共同儲存格 (是別人的)，所以只要判斷此格就好
            # 其他都是空的儲存格
            if pd.isnull(NextData[0]) and pd.isnull(Data[1]) and pd.isnull(NextData[1]):
                CurrentUserData["IsFilled"] = False
            elif not pd.isnull(NextData[0]) and pd.isnull(Data[1]):
                CurrentUserData["IsFilled"] = False
            else:
                CurrentUserData["IsFilled"] = True
            ExcelUserDataList.append(CurrentUserData)
    return ExcelUserDataList, True

# Main
UserData = ReadSettingJSON()
for podcasttime in PodcastTiming:
    if podcasttime == PodcastTiming[len(PodcastTiming) - 1]:
        # schedule.every().day.at(podcasttime).do(DoPodcastJob, True)
        schedule.every().minute.at(podcasttime).do(DoPodcastJob, True)
    else:
        # schedule.every().day.at(podcasttime).do(DoPodcastJob)
        schedule.every().minute.at(podcasttime).do(DoPodcastJob)
print("Start Podcast!!")
while True:
    schedule.run_pending()
    time.sleep(1)

# 測試是否能讀到 Excel
# print(ReadTodayExcel())