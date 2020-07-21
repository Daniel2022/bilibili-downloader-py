import requests
import json
import subprocess
import os
import http.cookiejar
import re
import pickle

GET_VIDEO_INFO_URL = "https://api.bilibili.com/x/web-interface/view"
GET_VIDEO_DOWNLOAD_URL = "https://api.bilibili.com/x/player/playurl"
GET_INFO_URL = "https://api.bilibili.com/x/space/acc/info"
GET_FAN_URL = "https://api.bilibili.com/x/relation/stat"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cookie": "",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.30 Safari/537.36 Edg/84.0.522.11",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": '1'
}

class MannualError(RuntimeError):
    def __init__(self,M):
        self.ErrorCode = M

def isNumber(keyword):
    try:
        int(keyword)
        return True
    except ValueError:
        return False   

def cookie_loader(cookiefile="cookies.sqlite"):
    #来自soimort/you-get sqlite格式火狐cookies处理
    import sqlite3, shutil, tempfile
    temp_dir = tempfile.gettempdir()
    temp_cookiefile = os.path.join(temp_dir, 'temp_cookiefile.sqlite')
    shutil.copy2(cookiefile, temp_cookiefile)
    cookies = http.cookiejar.MozillaCookieJar()
    con = sqlite3.connect(temp_cookiefile)
    cur = con.cursor()
    cur.execute("""SELECT host, path, isSecure, expiry, name, value
    FROM moz_cookies""")
    for item in cur.fetchall():
        c = http.cookiejar.Cookie(
            0, item[4], item[5], None, False, item[0],
            item[0].startswith('.'), item[0].startswith('.'),
            item[1], False, item[2], item[3], item[3] == '', None,
            None, {},
        )
        cookies.set_cookie(c)
    #引自mo-han/mo-han-toolbox
    cookie_dict = requests.utils.dict_from_cookiejar(cookies) 
    cookies_l = ['{}={}'.format(k, v) for k, v in cookie_dict.items()]
    cookie = '; '.join(cookies_l)
    return cookie

def set_header():
    if os.path.exists("cookies.sqlite"):
        headers['cookie'] = cookie_loader()
        print('已加载cookies')
    else:
        print('不存在cookies.sqlite')

def Download_Mission(url,referer,file_name=None):
    shell = "./aria2c.exe --continue=true \"" + url + "\" --referer=" + referer
    if file_name:
        shell += " -o \"" + file_name + "\""
    sbp = subprocess.Popen([r'powershell',shell])
    sbp.wait()
    if sbp.returncode:
        raise MannualError(1)

def title_generator(title:str):
    return title.replace("\\"," ").replace('/'," ").replace(":"," ")\
        .replace("*"," ").replace("?"," ").replace("\""," ").replace("<"," ")\
            .replace(">"," ").replace("|"," ").replace("”"," ").replace("“"," ")

def FFmpegMission(VideoName,AudioName,Outputname):
    shell = "./ffmpeg.exe -i \"" + VideoName + "\" -i \"" + AudioName + \
        "\" -c:v copy -c:a copy -strict experimental " + "\"" + Outputname + "\" -y"
    #print(shell)
    sbp = subprocess.Popen([r'powershell',shell])
    sbp.wait()
    if sbp.returncode:
        raise MannualError(2)
    else:
        subprocess.Popen("del \"" + VideoName + "\"", shell=True).wait()
        subprocess.Popen("del \"" + AudioName + "\"", shell=True).wait()

class bili_Video:
    def __init__(self,bvid=None,avid=None):
        response = requests.get(GET_VIDEO_INFO_URL, {
            "bvid": bvid,
            "aid": avid
        }).json()
        if response['code'] == 0:
            data = response['data']
            self.avid = data['aid']
            self.bvid = data['bvid']
            self.title = data['title']
            self.desc = data['desc']
            self.duration = data['duration']
            self.pages = data['videos']
            self.coin = data['stat']['coin']
            self.like = data['stat']['like']
            self.favorite = data['stat']['favorite']
            self.danmaku = data['stat']['danmaku']
            self.view = data['stat']['view']
            self.owner = UP(data['owner']['mid'])
            self.video_list = []
            count = 0
            for p in data['pages']:
                self.video_list.append(Videos(avid=self.avid,\
                    bvid=self.bvid,cid=p['cid'],page=count+1,title=self.title,subtitle=p['part']))
                count += 1
        else:
            raise MannualError(3)
    def show(self):
        string = "%s\nAV号：%s\nBV号：%s\nUP主：%s\nP数：%d\n\n" \
            % (self.title,self.avid,self.bvid,self.owner.name,self.pages)
        for i in range(self.pages):
            string += "P%d.%s\n" % (i+1,self.video_list[i].subtitle)
        return string

class Videos:
    def __init__(self,avid=None,bvid=None,cid=None,page=1,title=None,subtitle=None):
        self.avid = avid
        self.bvid = bvid
        self.cid = cid
        self.page = page
        self.title = title
        self.subtitle = subtitle
        self.referer = 'https://www.bilibili.com/video/%s?page=%d' % (self.bvid, self.page)
    def load(self):
        response = requests.get(GET_VIDEO_DOWNLOAD_URL,{
            'bvid': self.bvid,
            'cid': self.cid,
            'fourk': 1
        },headers=headers).json()
        if response['code'] == 0:
            data = response['data']
            self.duration = data['timelength']
            self.accept_quality = data['accept_quality']
            self.accept_desc = data['accept_description']
            self.AbleToDownload = True
        else:
            raise MannualError(3)
    def Flv_downloader(self,qn=80):
        if self.AbleToDownload:
            if qn in self.accept_quality:
                response = requests.get(GET_VIDEO_DOWNLOAD_URL,{
                    'bvid': self.bvid,
                    'cid': self.cid,
                    'fourk': 1,
                    'qn': qn
                },headers=headers).json()
                if response['code'] == 0:
                    data = response['data']
                    url = data['durl'][0]['url']
                    vformat = data['format']
                    file_name = title_generator(self.title) + "_" + str(self.page) + "_" + vformat + ".flv"
                    Download_Mission(url=url,file_name=file_name,referer=self.referer)
                else:
                    raise MannualError(3)
            else:
                raise MannualError(5)
        else:
            raise MannualError(4)
    def Dash_URL_extractor(self,qn=80):
        if self.AbleToDownload:
            if qn in self.accept_quality:
                response = requests.get(GET_VIDEO_DOWNLOAD_URL,{
                    'bvid': self.bvid,
                    'cid': self.cid,
                    'fourk': 1,
                    'qn': qn,
                    'fnval': 16
                },headers=headers).json()
                if response['code'] == 0:
                    data = response['data']
                    AUrl = data['dash']['audio'][0]['baseUrl']
                    self.tmp_DashUrl = DashUrlStruct(AUrl,qn)
                    counter = 0
                    for v in data['dash']['video']:
                        if v['id'] == qn:
                            self.tmp_DashUrl.AddVideoUrl(VUrl=v['baseUrl'],codecid=v['codecid'])
                            counter += 1
                        else:
                            continue
                        if counter >= 2:
                            break
                else:
                    raise MannualError(3)
            else:
                raise MannualError(5)
        else:
            raise MannualError(4)
    def Dash_downloader(self,codecid=7):
        filetitle = title_generator(self.title) + "_" + str(self.page)
        AudioName = filetitle + "_" + "Audio.aac"
        Download_Mission(self.tmp_DashUrl.AUrl,self.referer,AudioName)
        if codecid == 7:
            VideoName = filetitle + "_Video_AVC.mp4"
            Download_Mission(self.tmp_DashUrl.AVC_Url,self.referer,VideoName)
            Outputname = filetitle + "_AVC.mp4"
        elif codecid == 12 and self.tmp_DashUrl.HEVC:
            VideoName = filetitle + "_Video_HEV.mp4"
            Download_Mission(self.tmp_DashUrl.HEV_Url,self.referer,VideoName)
            Outputname = filetitle + "_HEV.mp4"
        else:
            raise MannualError(6)
        FFmpegMission(VideoName,AudioName,Outputname)
        del self.tmp_DashUrl
    def show(self):
        string = ''
        if self.AbleToDownload:
            #string += "可用画质\n"
            for i in range(len(self.accept_quality)):
                string += "%d.%s\n" % (i+1,self.accept_desc[i])
        else:
            raise MannualError(4)
        return string

class DashUrlStruct:
    def __init__(self,AUrl,qn):
        self.AUrl = AUrl
        self.HEVC = False
        self.qn = qn
    def AddVideoUrl(self,VUrl,codecid=7):
        if codecid == 12:
            self.HEV_Url = VUrl
            self.HEVC = True
            self.ready = True
        elif codecid == 7:
            self.AVC_Url = VUrl
            self.ready = True
        else:
            raise MannualError(6)

class UP:
    def __init__(self, mid):
        self.__mid = mid
        response = requests.get(GET_INFO_URL,{
            "mid": mid,
            "jsonp": "jsonp"
        }).json()
        if response['code'] == 0:
            self.name = response['data']['name']
            self.__level = response['data']['level']
            self.__sign = response['data']['sign']
        else:
            raise MannualError(3)
        response = requests.get(GET_FAN_URL,{
            'vmid': mid
        }).json()
        if response['code'] == 0:
            self.__follower = response['data']['follower']
        else:
            raise MannualError(3)
    def show(self):
        print('========UP主信息=======')
        print('ID:\t'+self.name)
        print('UID:\t'+str(self.__mid))
        print('等级:\tlv.'+str(self.__level))
        print('签名:\t'+self.__sign)
        print('粉丝:\t'+str(self.__follower))

"""交互部分"""
title = "\
██████╗ ██╗██╗     ██╗██████╗ ██╗██╗     ██╗    ██████╗  ██████╗ ██╗    ██╗██╗      ██████╗  █████╗ ██████╗ ███████╗██████╗ \n\
██╔══██╗██║██║     ██║██╔══██╗██║██║     ██║    ██╔══██╗██╔═══██╗██║    ██║██║     ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗\n\
██████╔╝██║██║     ██║██████╔╝██║██║     ██║    ██║  ██║██║   ██║██║ █╗ ██║██║     ██║   ██║███████║██║  ██║█████╗  ██████╔╝\n\
██╔══██╗██║██║     ██║██╔══██╗██║██║     ██║    ██║  ██║██║   ██║██║███╗██║██║     ██║   ██║██╔══██║██║  ██║██╔══╝  ██╔══██╗\n\
██████╔╝██║███████╗██║██████╔╝██║███████╗██║    ██████╔╝╚██████╔╝╚███╔███╔╝███████╗╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║\n\
╚═════╝ ╚═╝╚══════╝╚═╝╚═════╝ ╚═╝╚══════╝╚═╝    ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝"
ErrorMeassage = "按回车返回"
aria2ErrorMessage = "Error:Aria2未能开启下载\n可能原因：aria2c.exe不存在\n"
ffmpegErrorMessage = "Error:ffmpeg出错\n可能原因：ffmpeg.exe不存在\n"
APIErrorMessage = "Error:api获取错误\n可能原因：\n1.视频不可用\n2.使用非大会员帐号访问大会员专属视频\n"
VideoNotLoadMessage = "Error:Video实例未load\n[BUG]\n"
NotAcQnMessage = "Error:不可用画质\n[BUG]\n"
ParaMessage = "Error:参数不可用\n[BUG]\n"
StateErrorMessage = "Error:状态机错误\n[BUG]\n"
InputErrorMessgae = "Error:输入错误，请重新输入"

#主程序状态
NORMAL = 0
ADD_ITEM = 1
VideoInfo = 2
SELECT_QUALITY = 3
SELECT_CONTAINER = 4
FLV_DOWNLOADING = 5
SELECT_FORMAT = 6
AVC_DOWNLOADING = 7
HEV_DOWNLOADING = 8

item_group = []
STATE = NORMAL

av_pattern = re.compile(r'av[0-9]+',flags=re.I)
BV_pattern = re.compile(r'BV[0-9A-Za-z]+')

firststart = True

def exitAction():
    savedata = open('savedata','wb')
    pickle.dump(item_group,savedata)
    savedata.close()
    os.system('cls')
    print("脚本已退出，记录已保存至savedaata")
    os._exit(0)

class StateMachine:
    def __init__(self,state=NORMAL):
        self.statetag = state
        self.SelectedIndex = 0
        self.SelectedPIndex = 0
        self.keyword = None
        self.SelectedQuality = None
    def SetState(self,state):
        self.statetag = state
    def display(self):
        global firststart
        if not firststart and (not self.statetag == ADD_ITEM):
            os.system('cls')
            #print("Bilibili downloader")
            print(title)
        if self.statetag == NORMAL:
            if firststart:
                firststart = False
            print("待选稿件")
            index = 0
            for V in item_group:
                print("[%d] %s" % (index+1, V.title))
                index += 1
            print("添加稿件【A】 退出【Q】")
            print("选择一个稿件【输入数字1-%d】" % (index))
            
        elif self.statetag == VideoInfo:
            print("选择的稿件：")
            print(item_group[self.SelectedIndex].show())
            print("返回【X】 退出【Q】")
            print("选择要下载的P【1-%d】" % (item_group[self.SelectedIndex].pages))
        elif self.statetag == ADD_ITEM:
            print("返回【X】 退出【Q】")
            print("输入一个av号或BV号")
        elif self.statetag == SELECT_QUALITY:
            print("可用画质")
            print(item_group[self.SelectedIndex].video_list[self.SelectedPIndex].show())
            print("返回【X】 退出【Q】")
            print("选择画质【1-%d】" \
                % (len(item_group[self.SelectedIndex].video_list[self.SelectedPIndex].accept_quality)))
        elif self.statetag == SELECT_CONTAINER:
            print("退出【Q】")
            print("选择封装【1】FLV【2】MP4")
        elif self.statetag == FLV_DOWNLOADING:
            print("下载FLV封装……")
        elif self.statetag == SELECT_FORMAT:
            print("检测到该P有HEVC格式视频更省空间【Y/N】")
        elif self.statetag == AVC_DOWNLOADING:
            print("下载MP4封装AVC编码……")
        elif self.statetag == HEV_DOWNLOADING:
            print("下载MP4封装HEVC编码……")
        else:
            raise MannualError(8)
    def action(self):
        if self.statetag == NORMAL:
            self.keyword = input()
        elif self.statetag == ADD_ITEM:
            self.keyword = input()
            #while not self.keyword.lower() == 'x':
            if av_pattern.match(self.keyword):
                avid = re.search(r'[0-9]+',self.keyword)
                item_group.append(bili_Video(avid=int(avid.group(0))))
                print("已添加av%s" % avid.group(0))
            elif BV_pattern.match(self.keyword):
                bvid = BV_pattern.match(self.keyword)
                item_group.append(bili_Video(bvid=bvid.group(0)))
                print("已添加%s" % bvid.group(0))
            elif self.keyword.lower() == 'd':
                item_group.pop(len(item_group)-1)
            elif self.keyword.lower() == 'x' or self.keyword.lower() == 'q':
                pass
            else:
                raise MannualError(8)
        elif self.statetag == VideoInfo:
            self.keyword = input()
        elif self.statetag == SELECT_QUALITY:
            self.keyword = input()
        elif self.statetag == SELECT_CONTAINER:
            self.keyword = input()
        elif self.statetag == FLV_DOWNLOADING:
            item_group[self.SelectedIndex].video_list[self.SelectedPIndex].Flv_downloader(self.SelectedQuality)
        elif self.statetag == SELECT_FORMAT:
            self.keyword = input()
        elif self.statetag == AVC_DOWNLOADING:
            item_group[self.SelectedIndex].video_list[self.SelectedPIndex].Dash_downloader()
        elif self.statetag == HEV_DOWNLOADING:
            item_group[self.SelectedIndex].video_list[self.SelectedPIndex].Dash_downloader(12)
        else:
            raise MannualError(7)
    def switch(self):
        if self.keyword == 'q':
            exitAction()
        if self.statetag == NORMAL:
            if self.keyword.lower() == 'a':
                self.statetag = ADD_ITEM
            elif isNumber(self.keyword):
                self.SelectedIndex = int(self.keyword)-1
                self.statetag = VideoInfo
            else:
                raise MannualError(8)
            self.keyword = ""
            os.system('cls')
            #print("Bilibili downloader")
            print(title)
        elif self.statetag == ADD_ITEM:
            if self.keyword.lower() == 'x':
                self.statetag = NORMAL
        elif self.statetag == VideoInfo:
            if self.keyword.lower() == 'x':
                self.statetag = NORMAL
            elif isNumber(self.keyword):
                self.SelectedPIndex = int(self.keyword)-1
                item_group[self.SelectedIndex].video_list[self.SelectedPIndex].load()
                self.statetag = SELECT_QUALITY
            else:
                raise MannualError(8)
        elif self.statetag == SELECT_QUALITY:
            if self.keyword.lower() == 'x':
                self.statetag = VideoInfo
            elif isNumber(self.keyword):
                self.SelectedQuality = item_group[self.SelectedIndex].video_list[self.SelectedPIndex].accept_quality[int(self.keyword)-1]
                self.statetag = SELECT_CONTAINER
            else:
                raise MannualError(8)
        elif self.statetag == SELECT_CONTAINER:
            #print(self.statetag)
            if self.keyword.lower() == 'x':
                self.statetag = SELECT_QUALITY
                self.SelectedQuality = None
            elif isNumber(self.keyword):
                if int(self.keyword) == 1:
                    self.statetag = FLV_DOWNLOADING
                elif int(self.keyword) == 2:
                    item_group[self.SelectedIndex].video_list[self.SelectedPIndex].Dash_URL_extractor(self.SelectedQuality)
                    if item_group[self.SelectedIndex].video_list[self.SelectedPIndex].tmp_DashUrl.HEVC:
                        self.statetag = SELECT_FORMAT
                    else:
                        self.statetag = AVC_DOWNLOADING
                else:
                    raise MannualError(8)
            else:
                raise MannualError(8)
        elif self.statetag == SELECT_FORMAT:
            if self.keyword.lower() == 'x':
                self.statetag = SELECT_CONTAINER
            elif self.keyword.lower() == 'y':
                self.statetag = HEV_DOWNLOADING
            elif self.keyword.lower() == 'n':
                self.statetag = AVC_DOWNLOADING
            else:
                raise MannualError(8)
        elif self.statetag == AVC_DOWNLOADING or self.statetag == HEV_DOWNLOADING or \
            self.statetag == FLV_DOWNLOADING:
            self.statetag = VideoInfo
        else:
            raise MannualError(7)            

if __name__ == "__main__":
    
    #测试代码
    """
    #print(cookie_loader())
    set_header()
    #print(headers)
    v = bili_Video(bvid='BV13z4y1d79P')
    #v.owner.show()
    v.video_list[0].load()
    v.video_list[0].Dash_URL_extractor(qn=116)
    v.video_list[0].Dash_downloader(12)
    #v.video_list[0].Flv_downloader(116)
    """
    os.system('cls')
    #print("Bilibili downloader")
    print(title)
    PATH = os.environ['PATH'].split(os.pathsep)
    Aria2_Exist = os.path.isfile("aria2c.exe")
    FFmpeg_Exist = os.path.isfile("ffmpeg.exe")
    """
    for pathroute in PATH:
        Aria2_candidate = os.path.join(pathroute,'aria2c.exe')
        FFmpeg_candidate = os.path.join(pathroute,'ffmpeg.exe')
        if os.path.isfile(Aria2_candidate) and not Aria2_Exist:
            print("检测到Aria2")
            Aria2_Exist = True
        if os.path.isfile(FFmpeg_candidate) and not FFmpeg_Exist:
            print("检测到ffmpeg")
            FFmpeg_Exist = True
        if Aria2_Exist and FFmpeg_Exist:
            break
    """
    #检测aria2 和 ffmpeg
    if Aria2_Exist:
        print("检测到Aria2")
    else:
        print("未检测到aria2c.exe")
        os._exit(0)
    if FFmpeg_Exist:
        print("检测到ffmpeg")
    else:
        print("未检测到ffmpeg.exe")
        os._exit(0)
    #初始生成savedata
    if not os.path.isfile('savedata'):
        f = open('savedata',mode='wb')
        f.close()
        savedata = open('savedata','wb')
        pickle.dump([],savedata)
        savedata.close()
    else:#从savedata文件读取历史记录
        savedata = open('savedata','rb')
        item_group.extend(pickle.load(savedata))
        savedata.close()

    set_header() #读取cookie.sqlite
    State = StateMachine() #初始化状态机实例
    while(True):
        try:
            State.display() #主程序
            State.action()
            State.switch()
        except MannualError as e:
            os.system('cls')
            if e.ErrorCode == 1:
                print(aria2ErrorMessage)
            elif e.ErrorCode == 2:
                print(ffmpegErrorMessage)
            elif e.ErrorCode == 3:
                print(APIErrorMessage)
            elif e.ErrorCode == 4:
                print(VideoNotLoadMessage)
            elif e.ErrorCode == 5:
                print(NotAcQnMessage)
            elif e.ErrorCode == 6:
                print(ParaMessage)
            elif e.ErrorCode == 7:
                print(StateErrorMessage)
            elif e.ErrorCode == 8:
                print(InputErrorMessgae)
            else:
                print("Not Known")
            input(ErrorMeassage)
            if e.ErrorCode == 8:
                pass
            else:
                State.statetag = NORMAL
        except IndexError:
            print("Error:索引错误")
            input(ErrorMeassage)