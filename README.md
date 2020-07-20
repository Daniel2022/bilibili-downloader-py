# bilibili-downloader
支持哔哩哔哩FLV、MP4（AVC、HEVC编码）视频下载的python脚本<br>
可通过稿件av号BV获取全部画质（大会员需火狐cookie）的FLV，MP4封装视频<br>
其中MP4可选HEVC编码（有的话）<br>
## 如何使用
```shell
python downloader.py //shell
```
根据脚本文字提示使用
## 依赖
* [aria2](https://github.com/aria2/aria2)

* [ffmpeg](https://ffmpeg.org/)

以上软件需让可执行文件与脚本在一个文件夹

* python requests 模块
```shell
pip install requests
```
## 支持系统及python版本
Python 3<br>
目前仅支持 Windows（后期会支持Linux系统）
## Cookie使用
支持firefox浏览器的cookie.sqlite<br>
cookie文件和downloader.py放置在同一文件夹<br>
推荐加载带帐号的cookie，否则无法获取480p以上的FLV<br>
（MP4可以）
## 当前支持特性
+ 可添加多个视频实例至列表侯选
+ 支持保存添加过的视频实例至savedata二进制文件
## 待支持特性
+ 稿件多方面信息获取（实例属性已存在）
+ UP主信息获取
+ 所需环境自动初始化（Win & Linux）
+ 异常处理
+ 批量下载
+ 支持命令行带参数下载