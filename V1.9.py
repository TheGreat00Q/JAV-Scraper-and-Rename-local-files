# -*- coding:utf-8 -*-
import urllib.request, urllib, re, os, shutil, configparser, time, hashlib, json, requests
from PIL import Image
from tkinter import filedialog, Tk
from time import sleep


#get_directory功能是 获取用户选取的文件夹路径
def get_directory():
    directory_root = Tk()
    directory_root.withdraw()
    work_path = filedialog.askdirectory()
    if work_path == '':
        print('你没有选择目录! 请重新选：')
        sleep(2)
        get_directory()
    else:
        global path
        #askdirectory 获得是 正斜杠 路径C:/，所以下面要把 / 换成 反斜杠\
        path = work_path.replace('/', '\\')
        result_directory = '已选择文件夹：' + path + '\n'
        print(result_directory, '\n')
        record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
        record_txt.write(result_directory)
        record_txt.close()
        return


# 功能为记录错误txt
def write_fail(fail_m):
    print(fail_m, end='')
    record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
    record_txt.write(fail_m)
    record_txt.close()


# 打开url获取html
def get_html(url):
    qr = urllib.request.Request(url, headers=javlib_headers)
    ul = urllib.request.urlopen(qr, timeout=10)
    html = ul.read().decode('UTF-8')
    return html


# 调用百度翻译API接口
def tran(id, key, word):
    # init salt and final_sign
    salt = str(time.time())[:10]
    final_sign = id + word + salt + key
    final_sign = hashlib.md5(final_sign.encode("utf-8")).hexdigest()
    #表单paramas
    paramas = {
        'q': word,
        'from': 'jp',
        'to': 'zh',
        'appid': '%s' % id,
        'salt': '%s' % salt,
        'sign': '%s' % final_sign
    }
    response = requests.get('http://api.fanyi.baidu.com/api/trans/vip/translate', params=paramas).content
    content = str(response, encoding="utf-8")
    json_reads = json.loads(content)
    try:
        return(json_reads['trans_result'][0]['dst'])
    except:
        print('你的百度翻译账户正确吗？翻译失败！')
        return('翻译失败！')


# 测试javlib的Cookie是否失效，返回有用的cookie
def jav_cookie(url, user, jcook):
    headers = {'User-Agent': user, 'Cookie': jcook}  # 伪装成浏览器浏览网页
    print('正在测试javlib的Cookie是否有效...')
    try:
        rq = urllib.request.Request(url, headers=headers)
        urllib.request.urlopen(rq, timeout=10)
    except:
        try:  # 用网高峰期，经常打不开javlib，尝试第二次
            rq = urllib.request.Request(url, headers=headers)
            urllib.request.urlopen(rq, timeout=10)
        except:
            jcook = input("该Cookie已失效，请输入javlib的新Cookie:")
            headers = {'User-Agent': user, 'Cookie': jcook}  # 伪装成浏览器浏览网页
            config_s = configparser.RawConfigParser()
            config_s.read("命名格式和javlib网址配置文件.ini")
            config_s['打开浏览器->F12->F5->Ctrl C+V']['javlib的Cookie'] = jcook
            config_s.write(open('命名格式和javlib网址配置文件.ini', 'w'))
            jav_cookie(url, user, jcook)
    return headers


# 测试arzon的Cookie是否失效，返回有用的cookie
def arzon_cookie(user, acook):
    headers = {'User-Agent': user, 'Cookie': acook}  # 伪装成浏览器浏览网页
    print('正在测试arzon的Cookie是否有效...')
    try:
        rq = urllib.request.Request('https://www.arzon.jp/', headers=headers)
        ul = urllib.request.urlopen(rq, timeout=10)
        html = ul.read().decode('UTF-8')
    except:
        print('请检查你地网络连接再重开程序，无法连接arzon！')
        os.system('pause')
    adultg = re.search(r'(１８歳未満)', html)
    if str(adultg) != 'None':
        acook = input("该Cookie已失效，请输入arzon的新Cookie:")
        headers = {'User-Agent': user, 'Cookie': acook}  # 伪装成浏览器浏览网页
        config_s = configparser.RawConfigParser()
        try:
            config_s.read("命名格式和javlib网址配置文件.ini")
            config_s['打开浏览器->F12->F5->Ctrl C+V']['arzon的Cookie'] = acook
            config_s.write(open('命名格式和javlib网址配置文件.ini', 'w'))
        except:
            print('请关闭ini文件，再重开程序')
            os.system('pause')
        arzon_cookie(user, acook)
    return headers


#  main开始
# 读取配置文件，这个ini文件用来给用户设置重命名的格式和jav网址
config_settings = configparser.RawConfigParser()
print('正在读取ini中的设置...', end='')
try:
    config_settings.read("命名格式和javlib网址配置文件.ini")
    User = config_settings.get("打开浏览器->F12->F5->Ctrl C+V", "User-Agent")
    Jcook = config_settings.get("打开浏览器->F12->F5->Ctrl C+V", "javlib的Cookie")
    Acook = config_settings.get("打开浏览器->F12->F5->Ctrl C+V", "Arzon的Cookie")
    if_rename_mp4 = config_settings.get("重命名影片", "是否重命名影片？")
    rename_mp4 = config_settings.get("重命名影片", "重命名影片的格式")
    if_rename_folder = config_settings.get("重命名影片所在文件夹", "是否重命名文件夹？")
    rename_folder = config_settings.get("重命名影片所在文件夹", "重命名文件夹的格式")
    if_jpg = config_settings.get("获取三张jpg", "是否获取全标题的封面、fanart.jpg和poster.jpg？")
    javlib_easy_url = config_settings.get("其他设置", "javlib网址")
    suren_pref = config_settings.get("其他设置", "素人车牌(若有新车牌请自行添加)")
    file_type = config_settings.get("其他设置", "视频文件类型")
    if_tran = config_settings.get("百度翻译API", "是否需要中文简介？")
    ID = config_settings.get("百度翻译API", "APP ID")
    SK = config_settings.get("百度翻译API", "密钥")
except:
    try:
        config_settings.add_section("打开浏览器->F12->F5->Ctrl C+V")
        config_settings.set("打开浏览器->F12->F5->Ctrl C+V", "User-Agent", "")
        config_settings.set("打开浏览器->F12->F5->Ctrl C+V", "javlib的Cookie", "")
        config_settings.set("打开浏览器->F12->F5->Ctrl C+V", "Arzon的Cookie", "")
        config_settings.add_section("重命名影片")
        config_settings.set("重命名影片", "是否重命名影片？", "是")
        config_settings.set("重命名影片", "重命名影片的格式", "车牌")
        config_settings.add_section("重命名影片所在文件夹")
        config_settings.set("重命名影片所在文件夹", "是否重命名文件夹？", "是")
        config_settings.set("重命名影片所在文件夹", "重命名文件夹的格式", "【+首个女优+】+车牌")
        config_settings.add_section("获取三张jpg")
        config_settings.set("获取三张jpg", "是否获取全标题的封面、fanart.jpg和poster.jpg？", "是")
        config_settings.add_section("其他设置")
        config_settings.set("其他设置", "javlib网址", "http://c32r.com/cn/")
        config_settings.set("其他设置", "素人车牌(若有新车牌请自行添加)", "heyzo、mium、ntkara、gana、luxu、dcv、maan、hoi、nama、sweet、siro、scute、cute、sqb")
        config_settings.set("其他设置", "视频文件类型", "mp4、mkv、avi、wmv、iso、MP4、MKV、AVI、WMV、ISO")
        config_settings.add_section("百度翻译API")
        config_settings.set("百度翻译API", "是否需要中文简介？", "否")
        config_settings.set("百度翻译API", "APP ID", "")
        config_settings.set("百度翻译API", "密钥", "")
        config_settings.write(open("命名格式和javlib网址配置文件.ini", "w"))
        print('\n    >“命名格式和javlib网址配置文件.ini”文件被你玩坏了...正在重写ini...')
        print('写入“命名格式和javlib网址配置文件.ini”文件成功，如果需要修改重命名格式请重新打开ini修改，然后重新启动程序！')
        os.system('pause')
    except:
        print('\n这个ini文件被你写“死”了，删除它，然后打开exe自动重新创建ini！')
        os.system('pause')
print('\n读取ini文件成功! ')
# 用户选择文件夹
get_directory()
javlib_headers = jav_cookie(javlib_easy_url, User, Jcook)
print('当前javlib的Cookie有效！')
if if_tran == '是':
    arzon_headers = arzon_cookie(User, Acook)
    print('当前arzon的Cookie有效！')
fail_list = []                             #用于存放处理失败的信息
nfo_dict = {'空格': ' '}                   #用于暂时存放影片信息，女优，标题等
suren_list = suren_pref.split('、')        #素人番号的列表，来自ini文件的suren_pref
rename_mp4_list = rename_mp4.split('+')    #重命名格式的列表，来自ini文件的rename_mp4
type_tuple = tuple(file_type.split('、'))   #重命名格式的列表，来自ini文件的rename_mp4
number = 0                                 #已经处理文件的个数
fail_times = 0                             #处理过程中错失败的个数
#javlib上的av页面，获取主要信息
print('文件扫描开始...\n')
#root【当前路径】 dirs【子目录】 files【文件】，这三个都是列表
for root, dirs, files in os.walk(path):
    for file in files:
        number += 1
        if (number % 40) == 0:              #主要是防止假死，每扫描20个文件就提示一下
            print('【已扫描'+str(number)+'个文件，失败', fail_times, '个。】')
        # 判断是不是视频，得到车牌号
        if file.endswith(type_tuple):
            video_num_g = re.search(r'([a-zA-Z]{2,6})-? ?(\d{2,5})', file)    # 这个正则表达式匹配“车牌号”可能有点奇怪，
            if str(video_num_g) != 'None':                               # 如果你下过上千部片，各种参差不齐的命名，你就会理解我了。
                num_pref = video_num_g.group(1)
                num_suf = video_num_g.group(2)
                num_pref = num_pref.lower()
                car_num = num_pref + '-' + num_suf
                if num_pref in suren_list:                             #如果这是素人影片，告诉一下用户，它们需要另外处理
                    fail_times += 1
                    fail_message = '    >第' + str(fail_times) + '个失败！素人影片：' + root + '\\' + file + '\n'
                    fail_list.append(fail_message)
                    write_fail(fail_message)
                    continue
            else:
                continue
        else:
            continue

        #这个txt用于记录中途崩溃的点
        fail_message = '>>正在处理：' + root + '\\' + file + '\n'
        record_t = open('程序中途崩溃.txt', 'w', encoding="utf-8")
        record_t.write(fail_message)
        record_t.close()
        #获取nfo信息的javlib搜索网页
        javlib_url = javlib_easy_url + 'vl_searchbyid.php?keyword=' + car_num
        try:
            javlib_html = get_html(javlib_url)
        except:
            try:  #用网高峰期，经常打不开javlib，尝试第二次
                fail_message = '>>尝试打开javlib的搜索页面失败，正在尝试第二次打开...\n'
                print(fail_message, end='')
                javlib_html = get_html(javlib_url)
                print('    >第二次尝试成功！')
            except:
                if len(fail_list) > 0 and '已更换域名' in fail_list[-1] :
                    print('javlib的cookie失效！请重开程序')
                    print('\n当前文件夹整理中断，', end='')
                    if fail_times > 0:
                        print('失败', fail_times, '个!  ', path, '\n')
                        if len(fail_list) > 0:
                            for fail in fail_list:
                                print(fail, end='')
                    os.system('pause')
                fail_times += 1
                fail_message = '    >第' + str(fail_times) + '个失败！可能是网络不稳定,可能是javlib已更换域名，可能是cookie失效： ' + root + '\\' + file + '\n'
                fail_list.append(fail_message)
                write_fail(fail_message)
                continue
        #搜索结果的网页，大部分情况就是这个影片的网页，也有可能是多个结果的网页
        #尝试找标题，第一种情况：找得到，就是这个影片的网页
        title = re.search(r'<title>([a-zA-Z]{1,6}-\d{1,5}.+?) - JAVLibrary</title>', javlib_html)  # 匹配处理“标题”
        # 搜索结果就是AV的页面
        if str(title) != 'None':
            title = title.group(1)
        # 第二种情况：搜索结果可能是两个以上，所以这种匹配找不到标题，None！
        else:   # 继续找标题，但匹配形式不同，这是找“可能是多个结果的网页”上的第一个标题
            search_result = re.search(r'<a href="./\?v=javli(.+?)" title="', javlib_html)
            # 搜索有几个结果，用第一个AV的网页，打开它
            if str(search_result) != 'None':
                first_search_url = javlib_easy_url + '?v=javli' + search_result.group(1)
                try:
                    javlib_html = get_html(first_search_url)
                except:
                    fail_times += 1
                    fail_message = '    >第' + str(fail_times) + '个失败！打开搜索结果页面上的AV失败，网络不稳定： ' + first_search_url + '  ' + root + '\\' + file + '\n'
                    fail_list.append(fail_message)
                    write_fail(fail_message)
                    continue
                #找到标题，留着马上整理信息用
                title = re.search(r'<title>([a-zA-Z]{1,6}-\d{1,5}.+?) - JAVLibrary</title>', javlib_html)
                title = title.group(1)
            # 第三种情况：搜索不到这部影片，搜索结果页面什么都没有
            else:
                # print(javlib_url)
                fail_times += 1
                fail_message = '    >第' + str(fail_times) + '个失败！找不到AV信息，无码？新系列素人？年代久远？： ' + root + '\\' + file + '\n'
                fail_list.append(fail_message)
                write_fail(fail_message)
                continue

        # 处理影片的标题过长
        if len(title) > 50:
            title_easy = title[:50]
        else:
            title_easy = title
        #正则匹配 影片信息 开始！
        #title的开头是车牌号，而我想要后面的纯标题
        only_titleg = re.search(r'.+?-\d+?[a-z]? (.+)', title_easy) #这边匹配番号，[a-z]可能很奇怪，
        nfo_dict['标题'] = only_titleg.group(1)                     #但javlib上的标题的番号后面有时有一个奇怪的字母
        # 车牌号
        idg = re.search(r'(.+?-\d+?)[a-z]? .+?', title_easy)
        nfo_dict['车牌'] = idg.group(1)
        # 制作商
        makerg = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="maker_', javlib_html)
        if str(makerg) != 'None':
            nfo_dict['制作商'] = makerg.group(1)
        else:
            nfo_dict['制作商'] = '未知制作商'
        # 发行商
        studiog = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="label_', javlib_html)
        if str(studiog) != 'None':
            nfo_dict['发行商'] = studiog.group(1)
        else:
            nfo_dict['发行商'] = '未知发行商'
        # 上映日
        premieredg = re.search(r'<td class="text">(\d\d\d\d-\d\d-\d\d)</td>', javlib_html)
        if str(premieredg) != 'None':
            nfo_dict['发行年月日'] = premieredg.group(1)
            nfo_dict['发行年份'] = nfo_dict['发行年月日'][0:4]
        else:
            nfo_dict['发行年月日'] = '未知发行时间'
            nfo_dict['发行年份'] = '未知发行年份'
        # 片长 <td><span class="text">150</span> 分钟</td>
        runtimeg = re.search(r'<td><span class="text">(\d+?)</span> 分钟</td>', javlib_html)
        if str(runtimeg) != 'None':
            nfo_dict['片长'] = runtimeg.group(1)
        else:
            nfo_dict['片长'] = '未知时长'
        # 导演
        directorg = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="director', javlib_html)
        if str(directorg) != 'None':
            nfo_dict['导演'] = directorg.group(1)
        else:
            nfo_dict['导演'] = '未知导演'
        # 演员们 和 # 第一个演员
        actors = re.findall(r'rel="tag">(.+?)</a></span> <span id="', javlib_html)
        if len(actors) != 0:
            nfo_dict['全部女优'] = actors
            nfo_dict['首个女优'] = actors[0]
        else:
            nfo_dict['首个女优'] = '未知演员'
            nfo_dict['全部女优'] = ['未知演员']
        # 特点
        genre = re.findall(r'category tag">(.+?)</a></span><span id="genre', javlib_html)
        if len(genre) != 0:
            nfo_dict['genre'] = genre
        else:
            nfo_dict['genre'] = ['无特点']
        # DVD封面cover
        coverg = re.search(r'src="(.+?)" width="600" height="403"', javlib_html)  # 封面图片的正则对象
        if str(coverg) != 'None':
            nfo_dict['cover'] = coverg.group(1)
        else:
            nfo_dict['cover'] = '0'
        # 评分
        scoreg = re.search(r'&nbsp;<span class="score">\((.+?)\)</span>', javlib_html)
        if str(scoreg) != 'None':
            score = float(scoreg.group(1))
            score_five = (score - 4) * 5 / 3     # javlib上稍微有人关注的影片评分都是6分以上（10分制），强行把它差距拉大
            if score_five >= 0:
                score_five = '%.1f' % score_five
                nfo_dict['评分'] = str(score_five)
            else:
                nfo_dict['评分'] = '0'
        else:
            nfo_dict['评分'] = '0'
        # arzon的简介
        plot = ''
        if if_tran == '是':
            while True:
                arzon_url = 'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q=' + car_num
                # os.system('pause')
                try:
                    rq_html = urllib.request.Request(arzon_url, headers=arzon_headers)
                    lp_html = urllib.request.urlopen(rq_html, timeout=10)
                    search_html = lp_html.read().decode('UTF-8')
                except:
                    try:
                        rq_html = urllib.request.Request(arzon_url, headers=arzon_headers)
                        lp_html = urllib.request.urlopen(rq_html, timeout=10)
                        search_html = lp_html.read().decode('UTF-8')
                    except:
                        fail_times += 1
                        fail_message = '    >第' + str(
                            fail_times) + '个失败！连接arzon网站失败，可能是网络不稳定，可能是cookie失效： ' + root + '\\' + file + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
                        record_txt.write(fail_message)
                        record_txt.close()
                        plot = '暂无简介\n'
                        break
                # arzon第一次搜索AV  <dt><a href="https://www.arzon.jp/item_1376110.html" title="限界集落に越してきた人妻 ～村民達の慰みモノにされる日々～"><img src=
                AVs = re.findall(r'<a href="(.+?)" title=', search_html)
                # print(arzon_html)
                # 可能是几个AV的界面
                if len(AVs) != 0:
                    # 第一个AV网页
                    if_item_html = re.match(r'/item.+?', AVs[0])
                    # 是/item_1441697.html
                    if if_item_html:
                        av_url = 'https://www.arzon.jp' + AVs[0]
                        #################################################################################
                        try:
                            rq_html = urllib.request.Request(av_url, headers=arzon_headers)
                            lp_html = urllib.request.urlopen(rq_html, timeout=10)
                            first_html = lp_html.read().decode('UTF-8')
                        except:
                            try:
                                rq_html = urllib.request.Request(av_url, headers=arzon_headers)
                                lp_html = urllib.request.urlopen(rq_html, timeout=10)
                                first_html = lp_html.read().decode('UTF-8')
                            except:
                                fail_times += 1
                                fail_message = '    >第' + str(
                                    fail_times) + '个失败！无法进入第一个搜索结果： ' + root + '\\' + file + '\n'
                                print(fail_message, end='')
                                fail_list.append(fail_message)
                                record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
                                record_txt.write(fail_message)
                                record_txt.close()
                                plot = '暂无简介\n'
                                break
                        ############################################################################
                        plotg = re.search(r'<h2>作品紹介</h2>([\s\S]*?)</div>', first_html)
                        # 第一个页面找到plot
                        if str(plotg) != 'None':
                            plot = plotg.group(1)
                            plot_list = plot.split('<br />')
                            new = []
                            for line in plot_list:
                                line = line.strip()
                                new.append(line)
                            plot = ','.join(new)
                            plot = '中文简介：' + tran(ID, SK, plot) + '\n'
                        else:  # 第一个页面可能找不到，把第二个页面当做av_url
                            # 可能不存在第二个页面
                            if_item_url = re.match(r'/item.+?', AVs[1])
                            # 是不是/item_1441697.html
                            if if_item_url:
                                av_url = 'https://www.arzon.jp' + AVs[1]
                                #######################################################################
                                try:
                                    rq_html = urllib.request.Request(av_url, headers=arzon_headers)
                                    lp_html = urllib.request.urlopen(rq_html, timeout=10)
                                    second_html = lp_html.read().decode('UTF-8')
                                except:
                                    try:
                                        rq_html = urllib.request.Request(av_url, headers=arzon_headers)
                                        lp_html = urllib.request.urlopen(rq_html, timeout=10)
                                        second_html = lp_html.read().decode('UTF-8')
                                    except:
                                        fail_times += 1
                                        fail_message = '    >第' + str(
                                            fail_times) + '个失败！无法进入第二个搜索结果： ' + root + '\\' + file + '\n'
                                        print(fail_message, end='')
                                        fail_list.append(fail_message)
                                        record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
                                        record_txt.write(fail_message)
                                        record_txt.close()
                                        plot = '暂无简介\n'
                                        break
                                ############################################################################
                                plotg = re.search(r'<h2>作品紹介</h2>\s+?(.+?)\s{0,}<', second_html)
                                # 找到plot
                                if str(plotg) != 'None':
                                    plot = plotg.group(1)
                                    plot_list = plot.split('<br />')
                                    new = []
                                    for line in plot_list:
                                        line = line.strip()
                                        new.append(line)
                                    plot = ','.join(new)
                                    plot = '中文简介：' + tran(ID, SK, plot) + '\n'
                                else:  # 第二个页面可能找不到，把第三个页面当做av_url
                                    # 可能不存在第三个页面
                                    if_item_url = re.match(r'/item.+?', AVs[2])
                                    # 是不是/item_1441697.html
                                    if if_item_url:
                                        av_url = 'https://www.arzon.jp' + AVs[2]
                                        ############################################################################
                                        try:
                                            rq_html = urllib.request.Request(av_url, headers=arzon_headers)
                                            lp_html = urllib.request.urlopen(rq_html, timeout=10)
                                            third_html = lp_html.read().decode('UTF-8')
                                        except:
                                            try:
                                                rq_html = urllib.request.Request(av_url, headers=arzon_headers)
                                                lp_html = urllib.request.urlopen(rq_html, timeout=10)
                                                third_html = lp_html.read().decode('UTF-8')
                                            except:
                                                fail_times += 1
                                                fail_message = '    >第' + str(
                                                    fail_times) + '个失败！无法进入第三个搜索结果： ' + root + '\\' + file + '\n'
                                                print(fail_message, end='')
                                                fail_list.append(fail_message)
                                                record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
                                                record_txt.write(fail_message)
                                                record_txt.close()
                                                plot = '暂无简介\n'
                                        ############################################################################
                                        plotg = re.search(r'<h2>作品紹介</h2>\s+?(.+?)\s{0,}<', third_html)
                                        # 找到plot
                                        if str(plotg) != 'None':
                                            plot = plotg.group(1)
                                            plot_list = plot.split('<br />')
                                            new = []
                                            for line in plot_list:
                                                line = line.strip()
                                                new.append(line)
                                            plot = ','.join(new)
                                            plot = '中文简介：' + tran(ID, SK, plot) + '\n'
                                        else:  # 第三个搜索界面也找不到
                                            fail_times += 1
                                            fail_message = '    >第' + str(
                                                fail_times) + '个失败！有三个搜索结果，但找不到简介： ' + root + '\\' + file + '\n'
                                            print(fail_message, end='')
                                            fail_list.append(fail_message)
                                            record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
                                            record_txt.write(fail_message)
                                            record_txt.close()
                                            plot = '暂无简介\n'
                                            break
                                    # 第三个页面不是/item_1441697.html
                                    else:
                                        fail_times += 1
                                        fail_message = '    >第' + str(
                                            fail_times) + '个失败！有两个搜索结果，但找不到简介： ' + root + '\\' + file + '\n'
                                        print(fail_message, end='')
                                        fail_list.append(fail_message)
                                        record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
                                        record_txt.write(fail_message)
                                        record_txt.close()
                                        plot = '暂无简介\n'
                                        break
                            else:
                                # 第二个页面不是/item_1441697.html
                                fail_times += 1
                                fail_message = '    >第' + str(
                                    fail_times) + '个失败！有一个搜索结果，但找不到简介： ' + root + '\\' + file + '\n'
                                print(fail_message, end='')
                                fail_list.append(fail_message)
                                record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
                                record_txt.write(fail_message)
                                record_txt.close()
                                plot = '暂无简介\n'
                                break
                    # 第一个页面就不是/item_1441697.html，arzon搜索不到
                    else:
                        fail_times += 1
                        fail_message = '    >第' + str(
                            fail_times) + '个失败！arzon找不到该影片信息，可能被下架： ' + root + '\\' + file + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
                        record_txt.write(fail_message)
                        record_txt.close()
                        plot = '暂无简介\n'
                        break
                # arzon搜索页面实际是18岁验证
                else:
                    adultg = re.search(r'１８歳未満', search_html)
                    if str(adultg) != 'None':
                        fail_times += 1
                        fail_message = '    >第' + str(
                            fail_times) + '个失败！成人验证，请更新cookie： ' + root + '\\' + file + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
                        record_txt.write(fail_message)
                        record_txt.close()
                        plot = '暂无简介\n'
                        break
                    else:  # 不是成人验证，也没有结果
                        fail_times += 1
                        fail_message = '    >第' + str(
                            fail_times) + '个失败！不是成人验证，也找不到影片： ' + root + '\\' + file + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        record_txt = open('获取失败记录.txt', 'a', encoding="utf-8")
                        record_txt.write(fail_message)
                        record_txt.close()
                        plot = '暂无简介\n'
                        break
                break
            else:
                plot = '暂无简介\n'
        # javlib的精彩影评   (.+?\s*.*?\s*.*?\s*.*?)  不用影片简介，用jaclib上的精彩影片，下面的匹配可能很奇怪，没办法，就这么奇怪
        review = re.findall(r'(hidden">.+?</textarea>)</td>\s*?<td class="scores"><table>\s*?<tr><td><span class="scoreup">\d\d+?</span>', javlib_html, re.DOTALL)
        nfo_dict['plot_review'] = '\n精彩影评：'
        if len(review) != 0:
            sort_num = 0
            for rev in review:
                right_review = re.findall(r'hidden">(.+?)</textarea>', rev, re.DOTALL)
                if len(right_review) != 0:
                    nfo_dict['plot_review'] = nfo_dict['plot_review'] + right_review[-1] + '\n\n'
                    continue
        else:
            nfo_dict['plot_review'] = ''
        #print(nfo_dict['plot_review'])
        # 企划 javlib上没有企划set
        #写入nfo开始
        dep_dir = 0   # 信号量，用来判断是不是独立文件夹
        if if_rename_folder == '是':
            # 新文件夹名rename_folder
            new_folder_name = ''
            rename_folder_list = rename_folder.split('+')
            for j in rename_folder_list:
                if j not in nfo_dict:
                    new_folder_name = new_folder_name + j
                elif j != '全部女优':
                    new_folder_name = new_folder_name + nfo_dict[j]
                else:
                    new_folder_name = new_folder_name + ' '.join(nfo_dict[j])
            # 修改文件夹
            if len(dirs) == 0 or (                #这个影片所在的目录没有其他子目录（len = 0），
                    len(dirs) == 1 and (dirs[0] == '.actors' or dirs[0] == '.actor' or dirs[0] == 'actors')):
                newroot_list = root.split('\\')   #或者只有存放女优头像的一个子目录（actor）
                del newroot_list[-1]
                upper2_root = '\\'.join(newroot_list)
                new_root = upper2_root + '\\' + new_folder_name      #这个影片所在的文件夹就会被重命名
                dep_dir = 1                       #信号量dep_dir 置为1， 文件夹会被重命名
            else:
                dep_dir = 2                       #信号量dep_dir 置为2， 不是影片单独的文件夹
                new_root = root                   #目录保持不变
        else:
            dep_dir = 0                           #没有使用重命名文件夹的功能
            new_root = root
        info_path = root + '\\' + nfo_dict['车牌'] + '.nfo'      #nfo存放的地址
        fanart_path = new_root + '\\' + nfo_dict['车牌'] + '-fanart.jpg'  #nfo中fanart.jpg的地址，fanart就是DVD的封面
        poster_path = new_root + '\\' + nfo_dict['车牌'] + '-poster.jpg'  #nfo中poster.jpg的地址，poster就是DVD的封面的正面
        # 开始写入nfo，这nfo格式是参考的emby的nfo
        try:
            f = open(info_path, 'w', encoding="utf-8")
        except:
            break
        f.write("<movie>\n"
                "  <plot>" + plot + nfo_dict['plot_review'] + "</plot>\n"
                "  <title>" + title + "</title>\n"
                "  <director>" + nfo_dict['导演'] + "</director>\n"
                "  <rating>" + nfo_dict['评分'] + "</rating>\n"
                "  <year>" + nfo_dict['发行年份'] + "</year>\n"
                "  <mpaa>NC-17</mpaa>\n"
                "  <countrycode>JP</countrycode>\n"
                "  <premiered>" + nfo_dict['发行年月日'] + "</premiered>\n"
                "  <release>" + nfo_dict['发行年月日'] + "</release>\n"
                "  <runtime>" + nfo_dict['片长'] + "</runtime>\n"
                "  <country>日本</country>\n"
                "  <studio>" + nfo_dict['发行商'] + "</studio>\n"
                "  <art>\n    <poster>" + poster_path + "</poster>\n    <fanart>" + fanart_path +
                "</fanart>\n  </art>\n"
                "  <maker>" + nfo_dict['制作商'] + "</maker>\n"
                "  <id>" + nfo_dict['车牌'] + "</id>\n"
                "  <num>" + nfo_dict['车牌'] + "</num>\n"
                "  <fanart>" + fanart_path + "</fanart>\n"
                "  <poster>" + poster_path + "</poster>\n")
        for i in nfo_dict['genre']:
            f.write("  <genre>" + i + "</genre>\n")
        for i in nfo_dict['全部女优']:
            f.write("  <actor>\n    <name>" + i + "</name>\n    <type>Actor</type>\n    <thumb>" + root + "\\.actors\\"
                    + i + ".jpg" + "</thumb>\n  </actor>\n")
        f.write("<movie>\n")
        f.close()
        print(">>nfo收集完成: " + title)

        #需要下载三张图片
        if if_jpg == '是':
            # 下载海报的地址 cover
            cover_url = 'http:' + nfo_dict['cover']
            # 默认的 全标题.jpg封面
            cover_path = root + '\\' + title + '.jpg'
            # 下载 海报
            try:
                urllib.request.urlretrieve(cover_url, cover_path)
                #print(cover_path, cover_url)
            except:
                fail_message = '    >可能是网络不好，也可能是标题里有windows系统不允许的命名格式字符，如“/”。\n     下载AV封面失败, 正在尝试下载默认的 车牌.jpg封面： '
                fail_list.append(fail_message)
                write_fail(fail_message)
                # 尝试下载 车牌.jpg封面
                try:
                    cover_path = root + '\\' + nfo_dict['车牌'] + '.jpg'
                    urllib.request.urlretrieve(cover_url, cover_path)
                    fail_message = '    >下载默认的 车牌.jpg封面成功! 以上错误可忽略'
                    fail_list.append(fail_message)
                    write_fail(fail_message)
                except:
                    fail_times += 1
                    fail_message = '    >第' + str(fail_times) + '个失败！网络不好或者影片很老，没有800*538的封面。\n     下载AV封面失败, 下面的图片处理也会相应失败： ' + root + '\\' + file + '\n'
                    fail_list.append(fail_message)
                    write_fail(fail_message)
            # 下载cover成功，复制生成 fanart.jpg
            fan_path = root + '\\' + nfo_dict['车牌'] + '-fanart.jpg'
            try:
                shutil.copyfile(cover_path, fan_path)
                print('    >fanart.jpg保存成功')
            except:
                fail_times += 1
                fail_message = '    >第' + str(fail_times) + '个失败！fanart.jpg保存失败，请手动保存它吧： ' + root + '\\' + file + '\n'
                fail_list.append(fail_message)
                write_fail(fail_message)
            #fanart是800*538的jpg，切割fanart生成 poster.jpg，
            try:
                img = Image.open(cover_path)
                poster_path = root + '\\' + nfo_dict['车牌'] + '-poster.jpg'
                poster = img.crop((421, 0, 800, 538))
                poster.save(poster_path)
                print('    >poster.jpg保存成功')
            except:
                fail_times += 1
                fail_message = '    >第' + str(fail_times) + '个失败！poster.jpg保存失败，请手动保存它吧： ' + root + '\\' + file + '\n'
                fail_list.append(fail_message)
                write_fail(fail_message)

        #重命名影片
        if if_rename_mp4 == '是':
            # 新视频名rename_mp4
            new_mp4_name = ''
            for j in rename_mp4_list:
                if j not in nfo_dict:
                    new_mp4_name = new_mp4_name + j
                elif j != '全部女优':
                    new_mp4_name = new_mp4_name + nfo_dict[j]
                else:
                    new_mp4_name = new_mp4_name + ' '.join(nfo_dict[j])
            #print(new_mp4_name)
            try:
                os.rename(root + '\\' + file, root + '\\' + new_mp4_name + file[-4:])
                print('    >修改文件名完成')
            except:#标题里有windows系统不允许的命名格式字符，如“/”
                fail_message = '    >修改视频文件名失败，文件可能被后台打开，也可能是 标题 里有windows系统不允许的命名格式字符，如“/”： ' + root + '\\' + file + '\n     正在尝试以车牌重命名视频...\n'
                fail_list.append(fail_message)
                write_fail(fail_message)
                try:
                    os.rename(root + '\\' + file, root + '\\' + car_num + file[-4:])
                    fail_times += 1
                    fail_message = '    >第' + str(fail_times) + '个失败！按格式修改视频文件名失败，以车牌重命名视频文件完成\n'
                    fail_list.append(fail_message)
                    write_fail(fail_message)
                except:  # 标题里有windows系统不允许的命名格式字符，如“/”
                    fail_times += 1
                    fail_message = '    >第' + str(fail_times) + '个失败！修改视频文件名失败，文件真的被后台打开了： ' + root + '\\' + file + '\n'
                    fail_list.append(fail_message)
                    write_fail(fail_message)


        #重命名文件夹
        if dep_dir == 1:
            try:
                os.rename(root, new_root)
            except:
                fail_message = '    >修改文件夹名失败： ' + root + '\\' + file + '\n'
                fail_list.append(fail_message)
                write_fail(fail_message)
                print('     正在尝试把文件夹标记为错误文件夹...\n', end='')
                try:
                    new_root = upper2_root + '\\' + car_num + '！！！重命名失败'
                    os.rename(root, new_root)
                    fail_times += 1
                    fail_message = '    >第' + str(fail_times) + '个失败！' \
                                   '这部影片的标题或演员信息里有windows系统不允许的命名格式字符，如“/”，\n' \
                                   '     请根据nfo中的影片信息手动修改文件夹！已经把该文件夹标记为错误文件夹：' + new_root + '\n'
                    fail_list.append(fail_message)
                    write_fail(fail_message)
                    break
                except:
                    fail_times += 1
                    fail_message = '    >第' + str(
                        fail_times) + '个失败！重命名文件夹名失败，内部文件被后台打开了，或者已经有同番号的文件夹了： ' + root + '\\' + file + '\n'
                    fail_list.append(fail_message)
                    write_fail(fail_message)
                    break
            print('    >修改文件夹名完成')
        elif dep_dir == 2:
            fail_times += 1
            fail_message = '    >不是影片独立的文件夹，重命名失败：' + root + '\\' + file + '\n'
            fail_list.append(fail_message)
            write_fail(fail_message)
            break


# 把记录奔溃的txt去掉
try:
    os.remove('程序中途崩溃.txt')
except:
    print('请不要随便打开“程序中途崩溃.txt”。')

print('\n当前文件夹完成，', end='')
if fail_times > 0:
    print('失败', fail_times, '个!  ', path, '\n')
    if len(fail_list) > 0:
        for fail in fail_list:
            print(fail, end='')
    print('\n这些失败也会被记录在程序所在的文件夹内的 “txt”文本中’')
else:
    print('没有处理失败的AV，干得漂亮！  ', path, '\n')
os.system("pause")
