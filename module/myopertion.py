import subprocess, os

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

aria2shell = "./aria2c.exe"
ffmpegshell = "./ffmpeg.exe"

class ProcessError(RuntimeError):
    def __init__(self,M):
        self.ErrorCode = M
    def reminder(self):
        if self.ErrorCode == 1:
            return "Error:Aria2未能开启下载\n可能原因：aria2c.exe不存在\n"
        elif self.ErrorCode == 2:
            return "Error:ffmpeg出错\n可能原因：ffmpeg.exe不存在\n"
        else:
            return "Not Known"

def cookie_loader(cookiefile="cookies.sqlite"):
    #来自soimort/you-get sqlite格式火狐cookies处理
    import sqlite3, shutil, tempfile, requests, http.cookiejar
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
    return [cookie,cookie_dict['bili_jct']]

def set_header():
    if os.path.exists("cookies.sqlite"):
        headers['cookie'] = cookie_loader()[0]
        print('已加载cookies')
    else:
        print('不存在cookies.sqlite')

#检查系统
def checkpath():
    global aria2shell, ffmpegshell
    Aria2_Exist = False
    FFmpeg_Exist = False
    if os.path.isfile("aria2c.exe"):
        print("使用aria2c.exe")
        Aria2_Exist = True
    if os.path.isfile("ffmpeg.exe"):
        print("使用ffmpeg.exe")
        FFmpeg_Exist = True
    PATH = os.environ['PATH'].split(os.pathsep)
    if Aria2_Exist and FFmpeg_Exist:
        return
    for pathroute in PATH:
        Aria2_candidate = os.path.join(pathroute,'aria2c.exe')
        FFmpeg_candidate = os.path.join(pathroute,'ffmpeg.exe')
        if os.path.isfile(Aria2_candidate) and not Aria2_Exist:
            print("检测到环境变量存在aria2")
            aria2shell = "aria2c"
            Aria2_Exist = True
        if os.path.isfile(FFmpeg_candidate) and not FFmpeg_Exist:
            print("检测到环境变量存在ffmpeg")
            ffmpegshell = "ffmpeg"
            FFmpeg_Exist = True
        if Aria2_Exist and FFmpeg_Exist:
            return
    if not Aria2_Exist:
        print("不存在aria2")
        os._exit(0)
    if not FFmpeg_Exist:
        print("不存在ffmpeg\n无法合成MP4")

def Download_Mission(url,referer,file_name=None):
    if not os.path.isfile("downloads/"+file_name) or os.path.isfile("downloads/"+file_name+".aria2"):
        #shell = "./aria2c.exe --continue=true \"" + url + "\" --referer=" + referer
        shell = "%s -s 1 --continue=true \"%s\" --referer=%s --dir=./downloads" % (aria2shell, url, referer)
        if file_name:
            #shell += " -o \"" + file_name + "\""
            shell += " -o \"%s\"" % file_name
        sbp = subprocess.Popen([r'powershell',shell])
        sbp.wait()
        if sbp.returncode:
            raise ProcessError(1)

def FFmpegMission(VideoName,AudioName,Outputname):
    #shell = "./ffmpeg.exe -i \"" + VideoName + "\" -i \"" + AudioName + \
    #    "\" -c:v copy -c:a copy -strict experimental " + "\"" + Outputname + "\" -y"
    shell = "%s -i \"downloads/%s\" -i \"downloads/%s\" -c:v copy -c:a copy -strict experimental \"downloads/%s\" -y" %\
        (ffmpegshell, VideoName, AudioName, Outputname)
    #print(shell)
    sbp = subprocess.Popen([r'powershell',shell],stdout=subprocess.PIPE)
    sbp.wait()
    print(VideoName)
    if sbp.returncode:
        raise ProcessError(2)
    else:
        subprocess.Popen([r'powershell', "rm \"./downloads/%s\"" % VideoName]).wait()
        subprocess.Popen([r'powershell', "rm \"./downloads/%s\"" % AudioName]).wait()

def title_generator(title:str):
    return title.replace("\\","-").replace('/',"-").replace(":","-")\
        .replace("*","-").replace("?","-").replace("\"","-").replace("<","-")\
            .replace(">","-").replace("|","-").replace("”","-").replace("“","-")

def file_exist(dir,patch):
    import re
    if os.path.isdir(dir):
        filelist = os.listdir(dir)
        for name in filelist:
            if re.match(patch,name):
                if name + ".aria2" in filelist:
                    return None
                return name
            else:
                continue
            return None
    else:
        return None