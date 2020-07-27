from module.bililib import bili_Video, MannualError, quality_dict
from module.myopertion import set_header, checkpath, ProcessError
import re, pickle, os
"""交互部分"""
title = "\
██████╗ ██╗██╗     ██╗██████╗ ██╗██╗     ██╗    \n\
██╔══██╗██║██║     ██║██╔══██╗██║██║     ██║    \n\
██████╔╝██║██║     ██║██████╔╝██║██║     ██║    \n\
██╔══██╗██║██║     ██║██╔══██╗██║██║     ██║    \n\
██████╔╝██║███████╗██║██████╔╝██║███████╗██║    \n\
╚═════╝ ╚═╝╚══════╝╚═╝╚═════╝ ╚═╝╚══════╝╚═╝    "
ErrorMeassage = "按回车返回"
ContinueMessage = "按回车继续"

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
UP_INFO = 9
AutoDownload = 10
AllDownload = 11

item_group = []
STATE = NORMAL

av_pattern = re.compile(r'av[0-9]+',flags=re.I)
BV_pattern = re.compile(r'BV[0-9A-Za-z]+')

firststart = True

def save():
    savedata = open(savefile,'wb')
    pickle.dump(item_group,savedata)
    savedata.close()

def exitAction():
    save()
    os.system('cls')
    print("脚本已退出，记录已保存至" + savefile)
    os._exit(0)

def isNumber(keyword):
    try:
        int(keyword)
        return True
    except ValueError:
        return False

class StateError(RuntimeError):
    def __init__(self,M):
        self.ErrorCode = M
    def reminder(self):
        if self.ErrorCode == 7:
            return "Error:状态机错误\n[BUG]\n"
        elif self.ErrorCode == 8:
            return "Error:输入错误，请重新输入"
        else:
            return "Not Known"

class StateMachine:
    def __init__(self,state=NORMAL):
        self.statetag = state
        self.SelectedIndex = 0
        self.SelectedPIndex = 0
        self.keyword = None
        self.SelectedQuality = None
        self.auto = False
        self.allauto = False
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
            print("添加稿件【A】 下载全部【Z】 退出【Q】")
            print("选择一个稿件【输入数字1-%d】" % (index))
        elif self.statetag == VideoInfo:
            print("选择的稿件：")
            print(item_group[self.SelectedIndex].show())
            print("查看UP主信息【S】返回【X】 退出【Q】")
            print("选择要下载的P【1-%d】下载全部【A】" % (item_group[self.SelectedIndex].pages))
        elif self.statetag == AutoDownload:
            print("下载全部分页：%s" % item_group[self.SelectedIndex].title)
        elif self.statetag == AllDownload:
            print("下载全部稿件")
        elif self.statetag == ADD_ITEM:
            print("删除末尾【D】 清空【CL】 返回【X】 退出【Q】")
            print("输入1个或多个av号或BV号（空格分隔）")
        elif self.statetag == SELECT_QUALITY:
            if self.auto or self.allauto:
                print("可用画质（下载会自动择优）")
                for i in range(len(quality_dict['desp'])):
                    print("%d.%s" % (i+1,quality_dict['desp'][i]))
                print("")
                print("选择批量的画质【1-%d】" % len(quality_dict['value']))
            else:
                print("可用画质")
                print(item_group[self.SelectedIndex].video_list[self.SelectedPIndex].showqn())
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
        elif self.statetag == UP_INFO:
            print('========UP主信息=======')
            print(item_group[self.SelectedIndex].owner.show())
            print("返回【X】 退出【Q】")
        else:
            raise StateError(7)
    def action(self):
        global item_group
        if self.statetag == NORMAL:
            self.keyword = input().strip()
        elif self.statetag == ADD_ITEM:
            self.keyword = input().strip()
            #while not self.keyword.lower() == 'x':
            if av_pattern.match(self.keyword) or BV_pattern.match(self.keyword):
                code_list = self.keyword.split()
                for code in code_list:
                    av_match = av_pattern.match(code)
                    BV_match = BV_pattern.match(code)
                    if av_match:
                        avid = re.search(r'[0-9]+',code).group(0)
                        item = bili_Video(avid=int(avid))
                        item_group.append(item)
                        print("已添加av%s\n%s" % (avid,item.title))
                    elif BV_match:
                        bvid = BV_match.group(0)
                        item = bili_Video(bvid=bvid)
                        item_group.append(item)
                        print("已添加%s\n%s" % (bvid,item.title))
                save()
            elif self.keyword.lower() == 'd':
                item_group.pop(len(item_group)-1)
            elif self.keyword.lower() == 'cl':
                del item_group
                item_group = []
            elif self.keyword.lower() == 'x' or self.keyword.lower() == 'q':
                pass
            else:
                raise StateError(8)
        elif self.statetag == VideoInfo:
            self.keyword = input().strip()
        elif self.statetag == AutoDownload:
            item_group[self.SelectedIndex].autodownload(self.SelectedQuality)
            self.auto = False
            os.system('cls')
            print("全部分页已下载完成")
            input(ContinueMessage)
        elif self.statetag == AllDownload:
            for i in range(len(item_group)):
                item_group[i].autodownload(self.SelectedQuality)
            self.allauto = False
            os.system('cls')
            print("全部稿件已下载完成")
            input(ContinueMessage)
        elif self.statetag == SELECT_QUALITY:
            self.keyword = input().strip()
        elif self.statetag == SELECT_CONTAINER:
            self.keyword = input().strip()
        elif self.statetag == FLV_DOWNLOADING:
            name = item_group[self.SelectedIndex].video_list[self.SelectedPIndex].Flv_downloader(self.SelectedQuality)
            os.system('cls')
            print("FLV视频已下载到%s" % name)
            input(ContinueMessage)
        elif self.statetag == SELECT_FORMAT:
            self.keyword = input().strip()
        elif self.statetag == AVC_DOWNLOADING:
            name = item_group[self.SelectedIndex].video_list[self.SelectedPIndex].Dash_downloader()
            #os.system('cls')
            print("MP4（AVC）视频已下载到%s" % name)
            input(ContinueMessage)
        elif self.statetag == HEV_DOWNLOADING:
            name = item_group[self.SelectedIndex].video_list[self.SelectedPIndex].Dash_downloader(12)
            #os.system('cls')
            print("MP4（HEV）视频已下载到%s" % name)
            input(ContinueMessage)
        elif self.statetag == UP_INFO:
            self.keyword = input().strip()
        else:
            raise StateError(7)
    def switch(self):
        if self.keyword == 'q':
            exitAction()
        if self.statetag == NORMAL:
            if self.keyword.lower() == 'a':
                self.statetag = ADD_ITEM
            elif self.keyword.lower() == 'z':
                self.allauto = True
                self.statetag = SELECT_QUALITY
            elif isNumber(self.keyword):
                self.SelectedIndex = int(self.keyword)-1
                self.statetag = VideoInfo
            else:
                raise StateError(8)
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
            elif self.keyword.lower() == 's':
                self.statetag = UP_INFO
            elif self.keyword.lower() == 'a':
                self.statetag = SELECT_QUALITY
                self.auto = True
            elif isNumber(self.keyword):
                self.SelectedPIndex = int(self.keyword)-1
                item_group[self.SelectedIndex].video_list[self.SelectedPIndex].load()
                self.statetag = SELECT_QUALITY
            else:
                raise StateError(8)
        elif self.statetag == SELECT_QUALITY:
            if self.keyword.lower() == 'x':
                self.statetag = VideoInfo
            elif isNumber(self.keyword):
                if self.auto or self.allauto:
                    self.SelectedQuality = quality_dict['value'][int(self.keyword)-1]
                    if self.auto:
                        self.statetag = AutoDownload
                    elif self.allauto:
                        self.statetag = AllDownload
                else:
                    self.SelectedQuality = item_group[self.SelectedIndex].video_list[self.SelectedPIndex].accept_quality[int(self.keyword)-1]
                    self.statetag = SELECT_CONTAINER
            else:
                raise StateError(8)
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
                    raise StateError(8)
            else:
                raise StateError(8)
        elif self.statetag == SELECT_FORMAT:
            if self.keyword.lower() == 'x':
                self.statetag = SELECT_CONTAINER
            elif self.keyword.lower() == 'y':
                self.statetag = HEV_DOWNLOADING
            elif self.keyword.lower() == 'n':
                self.statetag = AVC_DOWNLOADING
            else:
                raise StateError(8)
        elif self.statetag == AVC_DOWNLOADING or self.statetag == HEV_DOWNLOADING or \
            self.statetag == FLV_DOWNLOADING or self.statetag == AutoDownload:
            self.statetag = VideoInfo
        elif self.statetag == UP_INFO:
            if self.keyword.lower() == 'x':
                self.statetag = VideoInfo
            else:
                raise StateError(8)
        elif self.statetag == AllDownload:
            self.statetag = NORMAL
        else:
            raise StateError(7)            

if __name__ == "__main__":
    print(title)
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
    checkpath()
    State = StateMachine() #初始化状态机实例
    while(True):
        try:
            State.display() #主程序
            State.action()
            State.switch()
        except (MannualError, ProcessError, StateError) as e :
            #os.system('cls')
            print(e.reminder())
            input(ErrorMeassage)
            if e.ErrorCode == 8:
                State.keyword = None
            else:
                State.statetag = NORMAL
        except IndexError:
            print("Error:索引错误")
            input(ErrorMeassage)
        except KeyboardInterrupt:
            exitAction()