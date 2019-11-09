# JAV-Scraper-and-Rename-local-files
收集jav元数据，并规范本地文件（夹）的格式。  
python3.7  使用pyinstaller打包成exe。

工作流程：  
1、用户选择文件夹，遍历路径下的所有文件。  
2、文件是jav，取车牌号，到javXXX网站搜索影片找到对应网页。  
3、获取网页源码找出“标题”“导演”“发行日期”等信息和DVD封面url。  
4、重命名影片文件。  
5、保存信息写入nfo。  
6、下载封面url作fanart.jpg，裁剪右半边作poster.jpg。  
7、重命名文件夹。  

目标效果：  
![image](https://github.com/junerain123/Collect-Info-and-Fanart-for-JAV-/blob/master/images/1.png)  
![image](https://github.com/junerain123/Collect-Info-and-Fanart-for-JAV-/blob/master/images/2.png)  
![image](https://github.com/junerain123/Collect-Info-and-Fanart-for-JAV-/blob/master/images/3.png)  

以下为ini中的用户设置：

[收集nfo]  
是否收集nfo？ = 是  
是否跳过已存在nfo的文件夹？ = 否  

[重命名影片]  
是否重命名影片？ = 是  
重命名影片的格式 = 车牌+空格+标题  

[重命名影片所在文件夹]  
是否重命名文件夹？ = 是  
重命名文件夹的格式 = 【+首个女优+】+车牌  

[获取两张jpg]  
是否获取fanart.jpg和poster.jpg？ = 是  

[其他设置]  
javlibrary网址 = http://www.x39n.com/cn/  
javbus网址 = https://www.buscdn.work/  
素人车牌(若有新车牌请自行添加) = MIUM、NTK、ARA、GANA、LUXU、DCV、MAAN、HOI、NAMA、SWEET、SIRO、SCUTE、CUTE、SQB  
视频文件类型 = mp4、mkv、avi、wmv、iso、MP4、MKV、AVI、WMV、ISO  

[色花堂]  
色花堂网址 = https://www.sdfasf.space/  
在下载种子时下载封面？ = 否  

[百度翻译API]  
是否需要中文简介？ = 否  
app id =   
密钥 =   
