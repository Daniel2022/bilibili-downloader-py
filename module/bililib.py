import requests
if __name__ == "__main__":
    from myopertion import headers, title_generator, Download_Mission, FFmpegMission
else:
    from .myopertion import headers, title_generator, Download_Mission, FFmpegMission

GET_VIDEO_INFO_URL = "https://api.bilibili.com/x/web-interface/view"
GET_VIDEO_DOWNLOAD_URL = "https://api.bilibili.com/x/player/playurl"
GET_INFO_URL = "https://api.bilibili.com/x/space/acc/info"
GET_FAN_URL = "https://api.bilibili.com/x/relation/stat"

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

quality_dict_file = { #这个不知道写来干吗
    120:"4K",
    116:"1080p60",
    74:"720p60",
    112:"1080p+",
    80:"1080p",
    64:"720p",
    32:"480p",
    16:"360p"
}

class MannualError(RuntimeError):
    ContinueMessage = "按回车继续"
    def __init__(self,M):
        self.ErrorCode = M
    def reminder(self):
        if self.ErrorCode == 3:
            return "Error:api获取错误\n可能原因：\n1.视频不可用\n2.使用非大会员帐号访问大会员专属视频\n"
        elif self.ErrorCode == 4:
            return "Error:Video实例未load\n[BUG]\n"
        elif self.ErrorCode == 5:
            return "Error:不可用画质\n[BUG]\n"
        elif self.ErrorCode == 6:
            return "Error:参数不可用\n[BUG]\n"
        else:
            return "Not Known"

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
                    quality = data['quality']
                    #file_name = title_generator(self.title) + "_" + str(self.page) + "_" + vformat + ".flv"
                    file_name = "%s/P%d_%s_%s.flv" % (title_generator(self.title),self.page,title_generator(self.subtitle),quality_dict_file[quality])
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
        #filetitle = title_generator(self.title) + "_" + str(self.page)
        filetitle = "%s/P%d_%s" % (title_generator(self.title),self.page,title_generator(self.subtitle))
        if self.tmp_DashUrl.AUrl:
            AudioName = filetitle + "_" + "A.aac"
            Download_Mission(self.tmp_DashUrl.AUrl,self.referer,AudioName)
        if codecid == 7:
            VideoName = filetitle + "_%s_AVC_V.mp4" % quality_dict_file[self.tmp_DashUrl.qn]
            Download_Mission(self.tmp_DashUrl.AVC_Url,self.referer,VideoName)
            Outputname = filetitle + "_%s_AVC.mp4" % quality_dict_file[self.tmp_DashUrl.qn]
        elif codecid == 12 and self.tmp_DashUrl.HEVC:
            VideoName = filetitle + "_%s_HEVC_V.mp4" % quality_dict_file[self.tmp_DashUrl.qn]
            Download_Mission(self.tmp_DashUrl.HEV_Url,self.referer,VideoName)
            Outputname = filetitle + "_%s_HEVC.mp4" % quality_dict_file[self.tmp_DashUrl.qn]
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