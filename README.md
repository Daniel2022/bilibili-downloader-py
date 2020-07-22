# bilibili-downloader
支持哔哩哔哩FLV、MP4（AVC、HEVC编码）视频下载的python脚本<br>
可通过稿件av号BV获取全部画质（大会员需火狐cookie）的FLV，MP4封装视频<br>
其中MP4可选HEVC编码（有的话）<br>
## 如何使用
```Bash
python main.py 
#使用会自动生成savefile.pysav文件
#根据脚本文字提示使用
#依赖module/bililib.py
```
`portable/downloader.py` 为单文件版本
## 依赖
* [aria2](https://github.com/aria2/aria2)

* [ffmpeg](https://ffmpeg.org/)

以上软件需让可执行文件与脚本（`main.py` or `downloader.py`）<br>
在同一目录下

* python requests 模块
```Bash
pip install requests
```
## 支持系统及Python版本
Python 3<br>
目前仅支持 Windows（后期会支持Linux系统）
## Cookie使用
支持firefox浏览器的`cookies.sqlite`<br>
`cookies.sqlite`文件和`main.py`放置在同一文件夹<br>
推荐加载带帐号的cookie，否则无法获取480p以上的FLV（MP4不受影响）
## 当前支持特性
+ 批量下载（单稿件全P FLV封装）
+ 可添加多个视频实例至列表侯选
+ 支持保存添加过的视频实例至savedata二进制文件
+ 异常提示
+ UP主信息获取
## 待支持特性
+ 稿件多方面信息获取（实例属性已存在）
+ 所需环境自动初始化（Win & Linux）
+ 批量下载（全列表）
+ 支持命令行带参数下载
+ 剧集下载
+ 批量添加稿件