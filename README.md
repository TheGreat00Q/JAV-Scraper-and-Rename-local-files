# JAV-Scraper-and-Rename-local-files
收集jav元数据，并规范本地文件（夹）的格式，为emby、kodi、jellyfin收集女优头像。  
python3.7  使用pyinstaller打包成exe。

[点击下载exe](https://github-production-release-asset-2e65be.s3.amazonaws.com/199952692/7d8c8080-160c-11ea-8c65-7a45c68897a0?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20191203%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20191203T124053Z&X-Amz-Expires=300&X-Amz-Signature=595f929f52337453a6aa3e206542f52a1be5d1d29fc7f1dd06f9e93d51935adb&X-Amz-SignedHeaders=host&actor_id=44168897&response-content-disposition=attachment%3B%20filename%3DV1.9.7%2B.JAVSDT.zip&response-content-type=application%2Foctet-stream)
  或者[从蓝奏云下载](https://www.lanzous.com/i7tpkcd)

[点击下载emby和kodi女优头像](https://github-production-release-asset-2e65be.s3.amazonaws.com/199952692/40b54680-12f9-11ea-94e9-4e37ce4bec6e?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20191203%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20191203T172215Z&X-Amz-Expires=300&X-Amz-Signature=5ecbd9367a7a1135692406957163464a7cfcc9bbd563151bcdc686cceed71aad&X-Amz-SignedHeaders=host&actor_id=44168897&response-content-disposition=attachment%3B%20filename%3Dactors.zip&response-content-type=application%2Foctet-stream)  
  [点击下载jellyfin女优头像](https://github-production-release-asset-2e65be.s3.amazonaws.com/199952692/abfe6180-15f4-11ea-9c0b-cf86d9dc383b?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20191203%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20191203T100311Z&X-Amz-Expires=300&X-Amz-Signature=f13c8e4bd8942884aefe015f369938186147544dfae227fdb07744c64754b655&X-Amz-SignedHeaders=host&actor_id=44168897&response-content-disposition=attachment%3B%20filename%3DPeople.zip&response-content-type=application%2Foctet-stream)  
如果链接失效，请进入[“release”](https://github.com/junerain123/JAV-Scraper-and-Rename-local-files/releases)下载。  

[没人的电报群](https://t.me/javsdtool)  
<a target="_blank" href="//shang.qq.com/wpa/qunwpa?idkey=79a735ccf11ed7f15481ae02f6a58f16315b8b424149455b4dc65868362f4b30">没人的企鹅群</a>  



工作流程：  
1、用户选择文件夹，遍历路径下的所有文件。  
2、文件是jav，取车牌号，到javXXX网站搜索影片找到对应网页。  
3、获取网页源码找出“标题”“导演”“发行日期”等信息和DVD封面url。  
4、重命名影片文件。 
5、重命名文件夹或建立独立文件夹。
6、保存信息写入nfo。  
7、下载封面url作fanart.jpg，裁剪右半边作poster.jpg。  
8、移动文件夹，完成归类。  

目标效果：  
![image](https://github.com/junerain123/Collect-Info-and-Fanart-for-JAV-/blob/master/images/1.png)  
![image](https://github.com/junerain123/Collect-Info-and-Fanart-for-JAV-/blob/master/images/2.png)  
![image](https://github.com/junerain123/Collect-Info-and-Fanart-for-JAV-/blob/master/images/3.jpg)  

以下为ini中的用户设置：  
  
[收集nfo]  
是否收集nfo？ = 是  
是否跳过已存在nfo的文件夹？ = 是  
是否收集javlibrary上的影评？ = 是  
  
[重命名影片]  
是否重命名影片？ = 是  
重命名影片的格式 = 车牌+空格+标题  
  
[修改文件夹]  
是否重命名或创建独立文件夹？ = 是  
新文件夹的格式 = 【+全部女优+】+车牌  

[归类影片]  
是否归类影片？ = 否  
归类的根目录 = 所选文件夹  
归类的标准 = 发行年份\首个女优  
  
[获取两张jpg]  
是否获取fanart.jpg和poster.jpg？ = 是  
是否采取群辉video station命名方式？ = 否  
  
[kodi专用]
是否收集女优头像 = 否  
  
[emby服务端]  
网址 = http://localhost:8096/  
api id = 12345678  

[其他设置]  
简繁中文？ = 简  
javlibrary网址 = http://www.x39n.com/  
javbus网址 = https://www.buscdn.work/  
素人车牌(若有新车牌请自行添加) = MIUM、NTK、ARA、GANA、LUXU、DCV、MAAN、HOI、NAMA、SWEET、SIRO、SCUTE、CUTE、SQB  
扫描文件类型 = mp4、mkv、avi、wmv、iso、rmvb、MP4、MKV、AVI、WMV、ISO、RMVB  

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
  
