# Collect-Info-and-Fanart-for-JAV-
Collect jav movies information, and finally build local movie library with emby.
python3.7

1、用户选择文件夹，遍历路径下的所有文件。
2、文件是jav，取车牌号，爬虫到javXXX网站搜索影片找到对应网页。
3、正则，找出“标题”“导演”“发行日期”等信息和DVD封面url。
4、保存信息写入nfo，下载图片。
5、重命名文件和文件夹，用户可以自定义。

注意事项：
        1、仅支持有码和heyzo。
        2、每一步可能的出错都有try except报告错误。
        3、如果还有报错，闪退，文件夹下有同车牌的视频。无法辨别CD1、CD2。
        
1. Users select folders and then traverse all files in the path.
2. If the file is jav, take the license plate number, and crawl to the javXXX website to search the movie and find the corresponding page.
3. Regular, find out information such as "title", "director", "release date" and DVD cover url.
4. Save information and write to nfo, download pictures.
5. Users can customize them how to rename files and folders .


Matters needing attention:
  1. Only code and heyzo are supported.
  2. There are try except reports for every possible error.
  3. If there are any errors, flip back. There are videos with the ID under the folder. CD1 and CD2 could not be distinguished.
