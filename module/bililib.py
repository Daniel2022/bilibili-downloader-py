import requests
import subprocess
import http.cookiejar

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

quality_dict = {"desp":[ #这个不知道写来干吗
    "超清 4K",
    "高清 1080P60",
    "高清 720P60",
    "高清 1080P+",
    "高清 1080P",
    "高清 720P",
    "清晰 480P",
    "流畅 360P"],
    "value":[120,116,74,112,80,64,32,16]
}

class MannualError(RuntimeError):
    def __init__(self,M):
        self.ErrorCode = M   

def cookie_loader(cookiefile="cookies.sqlite"):
    #来自soimort/you-get sqlite格式火狐cookies处理
    import sqlite3, shutil, tempfile, os
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
    import os
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
        string = "%s\nAV号：av%s\nBV号：%s\nUP主：%s\nP数：%d\n\n" \
            % (self.title,self.avid,self.bvid,self.owner.name,self.pages)
        for i in range(self.pages):
            string += "P%d.%s\n" % (i+1,self.video_list[i].subtitle)
        return string
    def autodownload(self,qn=80):
        for i in range(len(self.video_list)):
            if not self.video_list[i].AbleToDownload:
                self.video_list[i].load()
            self.video_list[i].Flv_downloader(qn=qn,auto=True)

class Videos:
    def __init__(self,avid=None,bvid=None,cid=None,page=1,title=None,subtitle=None):
        self.avid = avid
        self.bvid = bvid
        self.cid = cid
        self.page = page
        self.title = title
        self.subtitle = subtitle
        self.AbleToDownload = False
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
    def Flv_downloader(self,qn=80,auto=False):
        if self.AbleToDownload:
            if qn in self.accept_quality or auto:
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
                    return file_name
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
                    try:
                        AUrl = data['dash']['audio'][0]['baseUrl']
                    except TypeError:
                        AUrl = None
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
        if self.tmp_DashUrl.AUrl:
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
        if self.tmp_DashUrl.AUrl:
            FFmpegMission(VideoName,AudioName,Outputname)
            del self.tmp_DashUrl
            return Outputname
        else:
            del self.tmp_DashUrl
            return VideoName
    def showqn(self):
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
        string = "ID:\t%s\nUID:\t%d\n等级:\tlv.%d\n签名:\t%s\n粉丝数:\t%d\n" \
            % (self.name, self.__mid, self.__level, self.__sign, self.__follower)
        return string