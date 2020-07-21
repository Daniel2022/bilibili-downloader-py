from module.bililib import bili_Video, set_header, MannualError
import re, pickle, os
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

savefile = "savefile.pysav"

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
    savedata = open(savefile,'wb')
    pickle.dump(item_group,savedata)
    savedata.close()
    os.system('cls')
    print("脚本已退出，记录已保存至" + savefile)
    os._exit(0)

def isNumber(keyword):
    try:
        int(keyword)
        return True
    except ValueError:
        return False

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
    if not os.path.isfile(savefile):
        f = open(savefile,mode='wb')
        f.close()
        savedata = open(savefile,'wb')
        pickle.dump([],savedata)
        savedata.close()
    else:#从savedata文件读取历史记录
        savedata = open(savefile,'rb')
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