# JAV-Scraper-and-Rename-local-files
收集jav元数据，并规范本地文件（夹）的格式。  
python3.7  使用pyinstaller打包成exe。

[点击下载exe](https://github-production-release-asset-2e65be.s3.amazonaws.com/199952692/44ea9980-156f-11ea-982e-8341a851c801?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20191202%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20191202T175721Z&X-Amz-Expires=300&X-Amz-Signature=396a8dbf73ce1a06c7cd4c5a33a46ea4c33d8f5cb7d0990c35443ac0684cc806&X-Amz-SignedHeaders=host&actor_id=44168897&response-content-disposition=attachment%3B%20filename%3DV1.9.7%2B.JAVSDT.zip&response-content-type=application%2Foctet-stream)
或者[蓝奏云](https://www.lanzous.com/i7t1mti)


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
![image](https://github.com/junerain123/Collect-Info-and-Fanart-for-JAV-/blob/master/images/3.jpg)  

以下为ini中的用户设置：  

[收集nfo]  
是否收集nfo？ = 是  
是否跳过已存在nfo的文件夹？ = 否  

[重命名影片]  
是否重命名影片？ = 是  
重命名影片的格式 = 车牌  
  
[修改文件夹]  
是否重命名或创建独立文件夹？ = 否  
新文件夹的格式 = 【+全部女优+】+车牌  

[获取两张jpg]  
是否获取fanart.jpg和poster.jpg？ = 是  

[kodi专用]  
是否收集女优头像 = 否  

[emby服务端]  
网址 = http://localhost:8096/  
api id = 12345678  

[其他设置]  
javlibrary网址 = http://www.x39n.com/cn/  
javbus网址 = https://www.buscdn.work/  
素人车牌(若有新车牌请自行添加) = MIUM、NTK、ARA、GANA、LUXU、DCV、MAAN、HOI、NAMA、SWEET、SIRO、SCUTE、CUTE、SQB  
扫描文件类型 = mp4、mkv、avi、wmv、iso、rmvb、m2ts  

[百度翻译API]  
是否需要日语简介？ = 是  
是否翻译为中文？ = 否  
app id =     
密钥 =   

[百度人体检测]  
是否需要准确定位人脸的poster？ = 否  
appid =   
api key =   
secret key =   
  
