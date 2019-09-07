# -*- coding:utf-8 -*-
import re, os, configparser, time, hashlib, json, requests
from PIL import Image
from tkinter import filedialog, Tk
from time import sleep


# get_directory功能是 获取用户选取的文件夹路径
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
        # askdirectory 获得是 正斜杠 路径C:/，所以下面要把 / 换成 反斜杠\
        path = work_path.replace('/', '\\')
        result_directory = '已选择文件夹：' + path + '\n'
        print(result_directory)
        record_txt = open('【记得清理它】失败记录.txt', 'a', encoding="utf-8")
        record_txt.write(result_directory)
        record_txt.close()
        return


# 功能为记录错误txt
def write_fail(fail_m):
    record_txt = open('【记得清理它】失败记录.txt', 'a', encoding="utf-8")
    record_txt.write(fail_m)
    record_txt.close()


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
        return json_reads['trans_result'][0]['dst']
    except:
        print('    >获取中文简介失败，百度翻译抽风了！')
        return '翻译失败！'


# 获取一个arzon_cookie，返回cookie
def get_acook():
    session = requests.Session()
    session.get('https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww.arzon.jp%2F', timeout=5)
    return session.cookies.get_dict()


#  main开始
# 读取配置文件，这个ini文件用来给用户设置重命名的格式和jav网址
config_settings = configparser.RawConfigParser()
print('正在读取ini中的设置...', end='')
try:
    config_settings.read("ini的设置会影响所有exe的操作结果.ini")
    if_nfo = config_settings.get("收集nfo", "是否收集nfo？")
    if_mp4 = config_settings.get("重命名影片", "是否重命名影片？")
    rename_mp4 = config_settings.get("重命名影片", "重命名影片的格式")
    if_floder = config_settings.get("重命名影片所在文件夹", "是否重命名文件夹？")
    rename_folder = config_settings.get("重命名影片所在文件夹", "重命名文件夹的格式")
    if_jpg = config_settings.get("获取两张jpg", "是否获取fanart.jpg和poster.jpg？")
    jav_url = config_settings.get("其他设置", "javlibrary网址")
    suren_pref = config_settings.get("其他设置", "素人车牌(若有新车牌请自行添加)")
    file_type = config_settings.get("其他设置", "视频文件类型")
    if_tran = config_settings.get("百度翻译API", "是否需要中文简介？")
    ID = config_settings.get("百度翻译API", "APP ID")
    SK = config_settings.get("百度翻译API", "密钥")
except:
    try:
        print('\n    >“ini的设置会影响所有exe的操作结果.ini”文件丢失...正在重写ini...')
        config_settings.add_section("收集nfo")
        config_settings.set("收集nfo", "是否收集nfo？", "是")
        config_settings.add_section("重命名影片")
        config_settings.set("重命名影片", "是否重命名影片？", "是")
        config_settings.set("重命名影片", "重命名影片的格式", "车牌+空格+标题")
        config_settings.add_section("重命名影片所在文件夹")
        config_settings.set("重命名影片所在文件夹", "是否重命名文件夹？", "是")
        config_settings.set("重命名影片所在文件夹", "重命名文件夹的格式", "【+首个女优+】+车牌")
        config_settings.add_section("获取两张jpg")
        config_settings.set("获取两张jpg", "是否获取fanart.jpg和poster.jpg？", "是")
        config_settings.add_section("其他设置")
        config_settings.set("其他设置", "javlibrary网址", "http://www.w35p.com/cn/")
        config_settings.set("其他设置", "素人车牌(若有新车牌请自行添加)", "HEYZO、MIUM、NTK、ARA、GANA、LUXU、DCV、MAAN、HOI、NAMA、SWEET、SIRO、SCUTE、CUTE、SQB")
        config_settings.set("其他设置", "视频文件类型", "mp4、mkv、avi、wmv、iso、MP4、MKV、AVI、WMV、ISO")
        config_settings.add_section("色花堂")
        config_settings.set("色花堂", "色花堂网址", "https://www.sdfasf.space/")
        config_settings.set("色花堂", "在下载种子时下载封面？", "否")
        config_settings.add_section("百度翻译API")
        config_settings.set("百度翻译API", "是否需要中文简介？", "否")
        config_settings.set("百度翻译API", "APP ID", "")
        config_settings.set("百度翻译API", "密钥", "")
        config_settings.write(open("ini的设置会影响所有exe的操作结果.ini", "w"))
        print('写入“ini的设置会影响所有exe的操作结果.ini”文件成功，如果需要修改重命名格式请重新打开ini修改，然后重新启动程序！')
        os.system('pause')
    except:
        print('\n这个ini文件被你写“死”了，删除它，然后打开exe自动重新创建ini！')
        os.system('pause')
print('\n读取ini文件成功! ')
# 用户选择文件夹
get_directory()
if if_tran == '是':
    print('正在尝试通过arzon的成人验证...')
    try:
        acook = get_acook()
        print('通过arzon的成人验证！')
    except:
        print('请检查网络连接！再重启程序！')
        os.system('pause')
fail_list = []                             # 用于存放处理失败的信息
nfo_dict = {'空格': ' '}                   # 用于暂时存放影片信息，女优，标题等
suren_list = suren_pref.split('、')        # 素人番号的列表，来自ini文件的suren_pref
rename_mp4_list = rename_mp4.split('+')    # 重命名视频的格式，来自ini文件的rename_mp4
rename_folder_list = rename_folder.split('+')    # 重命名文件夹的格式，来自ini文件的rename_floder
type_tuple = tuple(file_type.split('、'))   # 视频文件的类型，来自ini文件的file_type
fail_times = 0                             # 处理过程中错失败的个数
print('文件扫描开始...如果时间过长，请检查网络或者避开夜晚高峰期...\n')
# root【当前根目录】 dirs【子目录】 files【文件】，root是字符串，后两个是列表
for root, dirs, files in os.walk(path):
    for file in files:
        # 判断是不是视频，得到车牌号
        if file.endswith(type_tuple):
            video_num_g = re.search(r'([a-zA-Z]{2,6})-? ?(\d{2,5})', file)    # 这个正则表达式匹配“车牌号”可能有点奇怪，
            if str(video_num_g) != 'None':                               # 如果你下过上千部片，各种参差不齐的命名，你就会理解我了。
                num_pref = video_num_g.group(1)
                num_suf = video_num_g.group(2)
                car_num = num_pref.upper() + '-' + num_suf
                if num_pref in suren_list:                             # 如果这是素人影片，告诉一下用户，它们需要另外处理
                    fail_times += 1
                    fail_message = '第' + str(fail_times) + '个失败！素人影片：' + root.strip(path) + '\n'
                    print('>>' + fail_message, end='')
                    fail_list.append('    >' + fail_message)
                    write_fail('>>' + fail_message)
                    continue
            else:
                continue
        else:
            continue

        # 获取nfo信息的javlibrary搜索网页
        search_url = jav_url + 'vl_searchbyid.php?keyword=' + car_num
        try:
            jav_rqs = requests.get(search_url, timeout=20)
            jav_rqs.encoding = 'utf-8'
            jav_html = jav_rqs.text
        except:
            try:  # 用网高峰期，经常打不开javlibrary，尝试第二次
                print('>>尝试打开“', search_url, '”搜索页面失败，正在尝试第二次打开...')
                jav_rqs = requests.get(search_url, timeout=20)
                jav_rqs.encoding = 'utf-8'
                jav_html = jav_rqs.text
                print('    >第二次尝试成功！')
            except:
                fail_times += 1
                fail_message = '    >第' + str(fail_times) + '个失败！可能是网络不稳定,请避开夜晚高峰期： ' + root.strip(path) + '\n'
                print(fail_message, end='')
                fail_list.append(fail_message)
                write_fail(fail_message)
                continue
        # 搜索结果的网页，大部分情况就是这个影片的网页，也有可能是多个结果的网页
        # 尝试找标题，第一种情况：找得到，就是这个影片的网页
        title = re.search(r'<title>([a-zA-Z]{1,6}-\d{1,5}.+?) - JAVLibrary</title>', jav_html)  # 匹配处理“标题”
        # 搜索结果就是AV的页面
        if str(title) != 'None':
            title = title.group(1)
        # 第二种情况：搜索结果可能是两个以上，所以这种匹配找不到标题，None！
        else:   # 继续找标题，但匹配形式不同，这是找“可能是多个结果的网页”上的第一个标题
            search_result = re.search(r'<a href="./\?v=javli(.+?)" title="', jav_html)
            # 搜索有几个结果，用第一个AV的网页，打开它
            if str(search_result) != 'None':
                first_search_url = jav_url + '?v=javli' + search_result.group(1)
                try:
                    jav_rqs = requests.get(first_search_url, timeout=10)
                    jav_rqs.encoding = 'utf-8'
                    jav_html = jav_rqs.text
                except:
                    fail_times += 1
                    fail_message = '    >第' + str(fail_times) + '个失败！打开javlibrary搜索结果页面上的AV失败，网络不稳定： ' + first_search_url + '\n'
                    print(fail_message, end='')
                    fail_list.append(fail_message)
                    write_fail(fail_message)
                    continue
                # 找到标题，留着马上整理信息用
                title = re.search(r'<title>([a-zA-Z]{1,6}-\d{1,5}.+?) - JAVLibrary</title>', jav_html).group(1)
            # 第三种情况：搜索不到这部影片，搜索结果页面什么都没有
            else:
                fail_times += 1
                fail_message = '第' + str(fail_times) + '个失败！找不到AV信息，无码？新系列素人？年代久远？： ' + root.strip(path) + '\n'
                print('>>' + fail_message, end='')
                fail_list.append('    >' + fail_message)
                write_fail('>>' + fail_message)
                continue

        print('>>正在处理：', title)
        # 处理影片的标题过长
        if len(title) > 50:
            title_easy = title[:50]
        else:
            title_easy = title
        # 正则匹配 影片信息 开始！
        # title的开头是车牌号，而我想要后面的纯标题
        nfo_dict['标题'] = re.search(r'.+?-\d+?[a-z]? (.+)', title_easy).group(1)   #这边匹配番号，[a-z]可能很奇怪，但javlib上的标题的番号后面有时有一个奇怪的字母
        # 车牌号
        nfo_dict['车牌'] = car_num
        # 制作商
        makerg = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="maker_', jav_html)
        if str(makerg) != 'None':
            nfo_dict['制作商'] = makerg.group(1)
        else:
            nfo_dict['制作商'] = '未知制作商'
        # 发行商
        studiog = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="label_', jav_html)
        if str(studiog) != 'None':
            nfo_dict['发行商'] = studiog.group(1)
        else:
            nfo_dict['发行商'] = '未知发行商'
        # 上映日
        premieredg = re.search(r'<td class="text">(\d\d\d\d-\d\d-\d\d)</td>', jav_html)
        if str(premieredg) != 'None':
            nfo_dict['发行年月日'] = premieredg.group(1)
            nfo_dict['发行年份'] = nfo_dict['发行年月日'][0:4]
        else:
            nfo_dict['发行年月日'] = '1970-01-01'
            nfo_dict['发行年份'] = '1970'
        # 片长 <td><span class="text">150</span> 分钟</td>
        runtimeg = re.search(r'<td><span class="text">(\d+?)</span> 分钟</td>', jav_html)
        if str(runtimeg) != 'None':
            nfo_dict['片长'] = runtimeg.group(1)
        else:
            nfo_dict['片长'] = '0'
        # 导演
        directorg = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="director', jav_html)
        if str(directorg) != 'None':
            nfo_dict['导演'] = directorg.group(1)
        else:
            nfo_dict['导演'] = '未知导演'
        # 演员们 和 # 第一个演员
        actors_prag = re.search(r'<td class="header">演员:(.+?)</td>', jav_html, re.DOTALL)
        if str(actors_prag) != 'None':
            actors = re.findall(r'rel="tag">(.+?)</a></span> <span id', actors_prag.group(1))
            if len(actors) != 0:
                nfo_dict['首个女优'] = actors[0]
                nfo_dict['全部女优'] = actors
            else:
                nfo_dict['全部女优'] = ['未知演员']
                nfo_dict['首个女优'] = '未知演员'
        else:
            nfo_dict['全部女优'] = ['未知演员']
            nfo_dict['首个女优'] = '未知演员'
        # 特点
        genres = re.findall(r'category tag">(.+?)</a></span><span id="genre', jav_html)
        if len(genres) != 0:
            nfo_dict['genres'] = genres
        else:
            nfo_dict['genres'] = ['无特点']
        # DVD封面cover
        coverg = re.search(r'src="(.+?)" width="600" height="403"', jav_html)  # 封面图片的正则对象
        if str(coverg) != 'None':
            nfo_dict['cover'] = coverg.group(1)
        else:
            nfo_dict['cover'] = ''
        # 评分
        scoreg = re.search(r'&nbsp;<span class="score">\((.+?)\)</span>', jav_html)
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
        # javlib的精彩影评   (.+?\s*.*?\s*.*?\s*.*?)  不用影片简介，用javlib上的精彩影片，下面的匹配可能很奇怪，没办法，就这么奇怪
        review = re.findall(r'(hidden">.+?</textarea>)</td>\s*?<td class="scores"><table>\s*?<tr><td><span class="scoreup">\d\d+?</span>', jav_html, re.DOTALL)
        nfo_dict['plot_review'] = ''
        if len(review) != 0:
            nfo_dict['plot_review'] = '\n精彩影评：'
            for rev in review:
                right_review = re.findall(r'hidden">(.+?)</textarea>', rev, re.DOTALL)
                if len(right_review) != 0:
                    nfo_dict['plot_review'] = nfo_dict['plot_review'] + right_review[-1] + '\n\n'
                    continue
        # arzon的简介 #########################################################
        plot = ''
        if if_tran == '是':
            while True:
                arzon_url = 'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q=' + car_num
                # os.system('pause')
                try:
                    az_rqs = requests.get(arzon_url, cookies=acook, timeout=10)
                    az_rqs.encoding = 'utf-8'
                    search_html = az_rqs.text
                except:
                    try:
                        print('    >尝试打开“', arzon_url, '”搜索页面失败，正在尝试第二次打开...')
                        az_rqs = requests.get(arzon_url, cookies=acook, timeout=10)
                        az_rqs.encoding = 'utf-8'
                        search_html = az_rqs.text
                        print('    >第二次尝试成功！')
                    except:
                        fail_times += 1
                        fail_message = '    >第' + str(
                            fail_times) + '个失败！连接arzon网站失败，可能是网络不稳定，可能是cookie失效： ' + root.strip(path) + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        write_fail(fail_message)
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
                            rqs = requests.get(av_url, cookies=acook, timeout=10)
                            rqs.encoding = 'utf-8'
                            first_html = rqs.text
                        except:
                            try:
                                print('    >尝试打开“', av_url, '”第一个AV页面失败，正在尝试第二次打开...')
                                rqs = requests.get(av_url, cookies=acook, timeout=10)
                                rqs.encoding = 'utf-8'
                                first_html = rqs.text
                                print('    >第二次尝试成功！')
                            except:
                                fail_times += 1
                                fail_message = '    >第' + str(
                                    fail_times) + '个失败！无法进入第一个搜索结果： ' + av_url + '  ' + root.strip(path) + '\n'
                                print(fail_message, end='')
                                fail_list.append(fail_message)
                                write_fail(fail_message)
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
                            break
                        else:  # 第一个页面可能找不到，把第二个页面当做av_url
                            # 可能不存在第二个页面
                            if_item_url = re.match(r'/item.+?', AVs[1])
                            # 是不是/item_1441697.html
                            if if_item_url:
                                av_url = 'https://www.arzon.jp' + AVs[1]
                                #######################################################################
                                try:
                                    rqs = requests.get(av_url, cookies=acook, timeout=10)
                                    rqs.encoding = 'utf-8'
                                    second_html = rqs.text
                                except:
                                    try:
                                        print('    >尝试打开“', av_url, ' ”第二个页面失败，正在尝试第二次打开...\n')
                                        rqs = requests.get(av_url, cookies=acook, timeout=10)
                                        rqs.encoding = 'utf-8'
                                        second_html = rqs.text
                                        print('    >第二次尝试成功！')
                                    except:
                                        fail_times += 1
                                        fail_message = '    >第' + str(
                                            fail_times) + '个失败！无法进入第二个搜索结果： ' + av_url + '  ' + root.strip(path) + '\n'
                                        print(fail_message, end='')
                                        fail_list.append(fail_message)
                                        write_fail(fail_message)
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
                                    break
                                else:  # 第二个页面可能找不到，把第三个页面当做av_url
                                    # 可能不存在第三个页面
                                    if_item_url = re.match(r'/item.+?', AVs[2])
                                    # 是不是/item_1441697.html
                                    if if_item_url:
                                        av_url = 'https://www.arzon.jp' + AVs[2]
                                        ############################################################################
                                        try:
                                            rqs = requests.get(av_url, cookies=acook, timeout=10)
                                            rqs.encoding = 'utf-8'
                                            third_html = rqs.text
                                        except:
                                            try:
                                                print('    >尝试打开“', av_url, '”第三个页面失败，正在尝试第二次打开...\n')
                                                rqs = requests.get(av_url, cookies=acook, timeout=10)
                                                rqs.encoding = 'utf-8'
                                                third_html = rqs.text
                                                print('    >第二次尝试成功！')
                                            except:
                                                fail_times += 1
                                                fail_message = '    >第' + str(
                                                    fail_times) + '个失败！无法进入第三个搜索结果： ' + av_url + '  ' + root.strip(path) + '\n'
                                                print(fail_message, end='')
                                                fail_list.append(fail_message)
                                                write_fail(fail_message)
                                                plot = '暂无简介\n'
                                                break
                                        ############################################################################
                                        plotg = re.search(r'<h2>作品紹介</h2>\s+?(.+?)\s*<', third_html)
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
                                            break
                                        else:  # 第三个搜索界面也找不到
                                            fail_times += 1
                                            fail_message = '    >第' + str(
                                                fail_times) + '个失败！有三个搜索结果，但找不到简介：' + root.strip(path) + '\n'
                                            print(fail_message, end='')
                                            fail_list.append(fail_message)
                                            write_fail(fail_message)
                                            plot = '暂无简介\n'
                                            break
                                    # 第三个页面不是/item_1441697.html
                                    else:
                                        fail_times += 1
                                        fail_message = '    >第' + str(
                                            fail_times) + '个失败！有两个搜索结果，但找不到简介：' + root.strip(path) + '\n'
                                        print(fail_message, end='')
                                        fail_list.append(fail_message)
                                        write_fail(fail_message)
                                        plot = '暂无简介\n'
                                        break
                            else:
                                # 第二个页面不是/item_1441697.html
                                fail_times += 1
                                fail_message = '    >第' + str(
                                    fail_times) + '个失败！有一个搜索结果，但找不到简介：' + root.strip(path) + '\n'
                                print(fail_message, end='')
                                fail_list.append(fail_message)
                                write_fail(fail_message)
                                plot = '暂无简介\n'
                                break
                    # 第一个页面就不是/item_1441697.html，arzon搜索不到
                    else:
                        fail_times += 1
                        fail_message = '    >第' + str(
                            fail_times) + '个失败！arzon找不到该影片信息，可能被下架：' + root.strip(path) + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        write_fail(fail_message)
                        plot = '暂无简介\n'
                        break
                # arzon搜索页面实际是18岁验证
                else:
                    adultg = re.search(r'１８歳未満', search_html)
                    if str(adultg) != 'None':
                        fail_times += 1
                        fail_message = '    >第' + str(
                            fail_times) + '个失败！成人验证，请重启程序： ' + root.strip(path) + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        write_fail(fail_message)
                        plot = '暂无简介\n'
                        os.system('pause')
                    else:  # 不是成人验证，也没有结果
                        fail_times += 1
                        fail_message = '    >第' + str(
                            fail_times) + '个失败！不是成人验证，也找不到影片： ' + arzon_url + '  ' + root.strip(path) + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        write_fail(fail_message)
                        plot = '暂无简介\n'
                        break
        #######################################################################
        nfo_dict['标题'] = nfo_dict['标题'].replace('\\', '#').replace('/', '#').replace(':', '：')\
            .replace('*', '#').replace('?', '？').replace('"', '#').replace('<', '【').replace('>', '】').replace('|', '#').rstrip(nfo_dict['首个女优'])
        # print(nfo_dict['标题'])
        # print(nfo_dict['首个女优'])

        # 重命名视频
        new_mp4 = root + '\\' + file[:-4]
        if if_mp4 == '是':  # 新文件名
            new_mp4 = root + '\\'
            for j in rename_mp4_list:
                if j not in nfo_dict:
                    new_mp4 = new_mp4 + j
                elif j != '全部女优':
                    new_mp4 = new_mp4 + nfo_dict[j]
                else:
                    new_mp4 = new_mp4 + ' '.join(nfo_dict[j])
            try:
                os.rename(root + '\\' + file, new_mp4 + file[-4:])
                print('    >修改文件名完成')
            except:
                fail_times += 1
                fail_message = '    >第' + str(fail_times) + '个失败！修改视频文件名失败，有多部同车牌视频，或者文件被后台打开了： ' + root.strip(path) + '\n'
                print(fail_message, end='')
                fail_list.append(fail_message)
                write_fail(fail_message)

        #写入nfo开始
        if if_nfo == '是':
            # 开始写入nfo，这nfo格式是参考的emby的nfo
            info_path = new_mp4 + '.nfo'      #nfo存放的地址
            try:
                f = open(info_path, 'w', encoding="utf-8")
            except:
                fail_times += 1
                fail_message = '    >第' + str(fail_times) + '个失败！写入nfo失败，文件被后台打开了： ' + info_path.strip(
                    path) + '\n'
                print(fail_message, end='')
                fail_list.append(fail_message)
                write_fail(fail_message)
                continue
            f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n"
                    "<movie>\n"
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
                    "  <maker>" + nfo_dict['制作商'] + "</maker>\n"
                    "  <id>" + car_num + "</id>\n"
                    "  <num>" + car_num + "</num>\n")
            for i in nfo_dict['genres']:
                f.write("  <genre>" + i + "</genre>\n")
            for i in nfo_dict['全部女优']:
                f.write("  <actor>\n    <name>" + i + "</name>\n    <type>Actor</type>\n    <thumb></thumb>\n  </actor>\n")
            f.write("</movie>\n")
            f.close()
            print('    >nfo收集完成')

        # 需要下载三张图片
        if if_jpg == '是':
            # 下载海报的地址 cover
            cover_url = 'http:' + nfo_dict['cover']
            # 默认的 全标题.jpg封面
            fanart_path = new_mp4 + '-fanart.jpg'
            # 下载 海报
            try:
                r = requests.get(cover_url, stream=True)
                with open(fanart_path, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
                print('    >fanart.jpg保存成功')
            except:
                try:
                    print('    >尝试下载“', cover_url, '”封面失败，正在尝试第二次下载...')
                    r = requests.get(cover_url, stream=True)
                    with open(fanart_path, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
                    print('    >第二次下载成功')
                except:
                    fail_times += 1
                    fail_message = '    >第' + str(fail_times) + '个失败！网络不好或者影片很老，没有800*538的封面。\n     下载AV封面失败, 下面的图片处理也会相应失败： ' + root.strip(path) + '\n'
                    print(fail_message, end='')
                    fail_list.append(fail_message)
                    write_fail(fail_message)
            # 切割生成 poster
            try:
                img = Image.open(fanart_path)
                poster_path = new_mp4 + '-poster.jpg'
                poster = img.crop((421, 0, 800, 538))
                poster.save(poster_path)
                print('    >poster.jpg保存成功')
            except:
                fail_times += 1
                fail_message = '    >第' + str(fail_times) + '个失败！poster.jpg保存失败，请手动切割它吧： ' + root.strip(path) + '\n'
                print(fail_message, end='')
                fail_list.append(fail_message)
                write_fail(fail_message)

        #重命名文件夹
        if if_floder == '是':
            # 新文件夹名rename_folder
            new_folder = ''
            for j in rename_folder_list:
                if j not in nfo_dict:
                    new_folder = new_folder + j
                elif j != '全部女优':
                    new_folder = new_folder + nfo_dict[j]
                else:
                    new_folder = new_folder + ' '.join(nfo_dict[j])
            # 修改文件夹
            if len(dirs) == 0 or (len(dirs) == 1 and dirs[0] == '.actors'): # 这个影片所在的目录没有其他子目录（len = 0），或者只有存放女优头像的一个子目录（actor）
                newroot_list = root.split('\\')
                del newroot_list[-1]
                upper2_root = '\\'.join(newroot_list)
                new_root = upper2_root + '\\' + new_folder  # 这个影片所在的文件夹就会被重命名
            else:
                fail_times += 1
                fail_message = '    >第' + str(
                    fail_times) + '个失败！不是独立的文件夹，重命名文件夹失败： ' + root.strip(path) + '\n'
                print(fail_message, end='')
                fail_list.append(fail_message)
                write_fail(fail_message)
                break
            try:
                os.rename(root, new_root)
            except:
                fail_times += 1
                fail_message = '    >第' + str(
                    fail_times) + '个失败！重命名文件夹名失败，内部文件被后台打开了，或者已经有同番号的文件夹了： ' + root.strip(path) + '\n'
                print(fail_message, end='')
                fail_list.append(fail_message)
                write_fail(fail_message)
                break
            print('    >修改文件夹名完成')


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
