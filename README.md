# bilibili-downloader
支持哔哩哔哩FLV、MP4（AVC、HEVC编码）视频下载的python脚本<br>
可通过稿件av号BV获取全部画质（大会员需火狐cookie）的FLV，MP4封装视频<br>
其中MP4可选HEVC编码（有的话）<br>
## 当前支持特性
+ 批量下载（单稿件全P & 全候选列表 仅FLV封装）
+ 批量添加稿件
+ 可添加多个视频实例至列表侯选
+ 支持保存添加过的视频实例至savedata二进制文件
+ 异常提示
+ UP主信息获取
## 如何使用
### Release
zip包含pyinstaller打包的exe<br>
无需另外安装Python以及[aria2](https://github.com/aria2/aria2)，[ffmpeg](https://ffmpeg.org/)<br>
文件保存在`downloads`文件夹
### 使用源码
```Powershell
git clone https://github.com/Daniel2022/bilibili-downloader-py.git
cd bilibili-downloader-py
python main.py 
#使用会自动生成savefile.pysav文件
#根据脚本文字提示使用
#依赖module/bililib.py
```
## Cookie使用
支持firefox浏览器的`cookies.sqlite`<br>
`cookies.sqlite`文件和主程序（`downloader-x86(-64).exe`）放置在同一文件夹<br>
推荐加载带帐号的cookie，否则无法获取480p以上的FLV（MP4不受影响）
## 使用的开源软件
* [aria2](https://github.com/aria2/aria2)

* [ffmpeg](https://ffmpeg.org/)

## 源码运行环境
### Python环境
`Python 3.6` + `requests`模块（pyinstaller打包环境）
```Bash
pip install requests #安装模块
```
### OS
当前仅适用Windows（主要是在调用aria2和ffmpeg的函数）
```Python
#Code: /module/myopertion.py
def Download_Mission(url,referer,file_name=None):
    ...
def FFmpegMission(VideoName,AudioName,Outputname):
    ...
```
## 待支持特性
+ 稿件多方面信息获取（实例属性已存在）
+ 所需环境自动初始化（Win & Linux）
+ 支持命令行带参数下载
+ 剧集下载