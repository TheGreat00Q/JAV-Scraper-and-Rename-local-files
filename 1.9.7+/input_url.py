# -*- coding:utf-8 -*-
import requests, re, os, configparser, time, hashlib, json, shutil
from PIL import Image


# 调用百度翻译API接口
def tran(api_id, key, word, to_lang):
    # init salt and final_sign
    salt = str(time.time())[:10]
    final_sign = api_id + word + salt + key
    final_sign = hashlib.md5(final_sign.encode("utf-8")).hexdigest()
    #表单paramas
    paramas = {
        'q': word,
        'from': 'jp',
        'to': to_lang,
        'appid': '%s' % api_id,
        'salt': '%s' % salt,
        'sign': '%s' % final_sign
    }
    response = requests.get('http://api.fanyi.baidu.com/api/trans/vip/translate', params=paramas, timeout=10).content
    content = str(response, encoding="utf-8")
    json_reads = json.loads(content)
    try:
        return json_reads['trans_result'][0]['dst']
    except:
        print('    >正在尝试重新日译中...')
        return tran(api_id, key, word)


# 获取一个arzon_cookie，返回cookie
def get_acook():
    session = requests.Session()
    session.get('https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww.arzon.jp%2F', timeout=10)
    return session.cookies.get_dict()


#  main开始
#  main开始
print('1、避开12:00-14：00和18:00-1:00，访问javlibrary和arzon很慢。\n'
      '2、简体繁体取决于复制粘贴的网址是cn还是tw！\n')
# 读取配置文件，这个ini文件用来给用户设置重命名的格式和jav网址
config_settings = configparser.RawConfigParser()
print('正在读取ini中的设置...', end='')
try:
    config_settings.read('ini的设置会影响所有exe的操作结果.ini')
    if_nfo = config_settings.get("收集nfo", "是否收集nfo？")
    if_mp4 = config_settings.get("重命名影片", "是否重命名影片？")
    rename_mp4 = config_settings.get("重命名影片", "重命名影片的格式")
    if_jpg = config_settings.get("获取两张jpg", "是否获取fanart.jpg和poster.jpg？")
    if_qunhui = config_settings.get("获取两张jpg", "是否采取群辉video station命名方式？")
    if_sculpture = config_settings.get("kodi专用", "是否收集女优头像")
    simp_trad = config_settings.get("其他设置", "简繁中文？")
    bus_url = config_settings.get("其他设置", "javbus网址")
    if_plot = config_settings.get("百度翻译API", "是否需要日语简介？")
    if_tran = config_settings.get("百度翻译API", "是否翻译为中文？")
    ID = config_settings.get("百度翻译API", "APP ID")
    SK = config_settings.get("百度翻译API", "密钥")
except:
    print('\nini文件无法读写，使用“【有码】基于javlibrary.exe”重新创建ini！')
    os.system('pause')

if if_sculpture == '是':
    if not os.path.exists('女优头像'):
        print('\n“女优头像”文件夹丢失！请把它放进exe的文件夹中！\n')
        os.system('pause')
    if not os.path.exists('【缺失的女优头像统计For Kodi】.ini'):
        config_actor = configparser.ConfigParser()
        config_actor.add_section("缺失的女优头像")
        config_actor.set("缺失的女优头像", "女优姓名", "N(次数)")
        config_actor.add_section("说明")
        config_actor.set("说明", "上面的“女优姓名 = N(次数)”的表达式", "后面的N数字表示你有N部(次)影片都在找她的头像，可惜找不到")
        config_actor.set("说明", "你可以去保存一下她的头像jpg到“女优头像”文件夹", "以后就能保存她的头像到影片的文件夹了")
        config_actor.write(open('【缺失的女优头像统计For Kodi】.ini', "w"))
        print('\n    >“【缺失的女优头像统计For Kodi】.ini”文件被你玩坏了...正在重写ini...成功！')
        print('正在重新读取...', end='')

print('\n读取ini文件成功! ')

if simp_trad == '简':
    t_lang = 'zh'
else:
    t_lang = 'cht'

if if_plot == '是':
    print('正在尝试通过arzon的成人验证...')
    try:
        acook = get_acook()
        print('通过arzon的成人验证！')
    except:
        print('连接arzon失败，请避开网络高峰期！请重启程序！')
        os.system('pause')
# 用户选择文件夹
rename_mp4_list = rename_mp4.split('+')    #重命名格式的列表，来自ini文件的rename_mp4
root = os.path.join(os.path.expanduser("~"), 'Desktop')
#root【当前路径】 dirs【子目录】 files【文件】，这三个都是列表
#获取nfo信息的javlib搜索网页
while 1:
    nfo_dict = {'空格': ' '}                   #用于暂时存放影片信息，女优，标题等
    javlib_url = input('\n请输入javlibrary上的网址：')
    print()
    try:
        jav_rqs = requests.get(javlib_url, timeout=10)
        jav_rqs.encoding = 'utf-8'
        javlib_html = jav_rqs.text
    except:
        try:  #用网高峰期，经常打不开javlib，尝试第二次
            print('>>尝试打开页面失败，正在尝试第二次打开...\n')
            jav_rqs = requests.get(javlib_url, timeout=10)
            jav_rqs.encoding = 'utf-8'
            javlib_html = jav_rqs.text
            print('    >第二次尝试成功！')
        except:
            print('>>网址正确吗？打不开啊！')
            continue
    #搜索结果的网页，大部分情况就是这个影片的网页，也有可能是多个结果的网页
    #尝试找标题，第一种情况：找得到，就是这个影片的网页[a-zA-Z]{1,6}-\d{1,5}.+?
    titleg = re.search(r'<title>(.+?) - JAVLibrary</title>', javlib_html)  # 匹配处理“标题”
    # 搜索结果就是AV的页面
    if str(titleg) != 'None':
        title = titleg.group(1)
    # 第二种情况：搜索结果可能是两个以上，所以这种匹配找不到标题，None！
    else:   # 继续找标题，但匹配形式不同，这是找“可能是多个结果的网页”上的第一个标题
        print('>>网址正确吗？找不到影片信息啊！')
        continue

    # 去除title中的特殊字符
    title = title.replace('\n', '').replace('&', '和').replace('\\', '#').replace('/', '#')\
        .replace(':', '：').replace('*', '#').replace('?', '？').replace('"', '#').replace('<', '【')\
        .replace('>', '】').replace('|', '#').replace('＜', '【').replace('＞', '】')
    # 处理影片的标题过长
    if len(title) > 50:
        title_easy = title[:50]
    else:
        title_easy = title
    # 正则匹配 影片信息 开始！
    # title的开头是车牌号，而我想要后面的纯标题
    car_titleg = re.search(r'(.+?) (.+)', title_easy) #这边匹配番号，[a-z]可能很奇怪，
    nfo_dict['标题'] = car_titleg.group(2)
    nfo_dict['车牌'] = car_titleg.group(1)
    if nfo_dict['车牌'].startswith('T-28'):
        nfo_dict['车牌'] = nfo_dict['车牌'].replace('T-28', 'T28-', 1)
    print('>>正在处理：', title)
    # 片商
    studiog = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="maker_', javlib_html)
    if str(studiog) != 'None':
        nfo_dict['片商'] = studiog.group(1)
    else:
        nfo_dict['片商'] = '未知片商'
    # 上映日
    premieredg = re.search(r'<td class="text">(\d\d\d\d-\d\d-\d\d)</td>', javlib_html)
    if str(premieredg) != 'None':
        nfo_dict['发行年月日'] = premieredg.group(1)
        nfo_dict['发行年份'] = nfo_dict['发行年月日'][0:4]
        nfo_dict['月'] = nfo_dict['发行年月日'][5:7]
        nfo_dict['日'] = nfo_dict['发行年月日'][8:10]
    else:
        nfo_dict['发行年月日'] = '1970-01-01'
        nfo_dict['发行年份'] = '1970'
        nfo_dict['月'] = '01'
        nfo_dict['日'] = '01'
    # 片长 <td><span class="text">150</span> 分钟</td>
    runtimeg = re.search(r'<td><span class="text">(\d+?)</span>', javlib_html)
    if str(runtimeg) != 'None':
        nfo_dict['片长'] = runtimeg.group(1)
    else:
        nfo_dict['片长'] = '0'
    # 导演
    directorg = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="director', javlib_html)
    if str(directorg) != 'None':
        nfo_dict['导演'] = directorg.group(1)
    else:
        nfo_dict['导演'] = '未知导演'
    # 演员们 和 # 第一个演员
    actors_prag = re.search(r'<span id="cast(.+?)</td>', javlib_html, re.DOTALL)
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
    nfo_dict['标题'] = nfo_dict['标题'].rstrip(nfo_dict['首个女优'])
    # 特点
    genres = re.findall(r'category tag">(.+?)</a></span><span id="genre', javlib_html)
    if len(genres) == 0:
        genres = ['无特点']
    # DVD封面cover
    coverg = re.search(r'src="(.+?)" width="600" height="403"', javlib_html)  # 封面图片的正则对象
    if str(coverg) != 'None':
        cover = coverg.group(1)
    else:
        cover = ''
    # 评分
    scoreg = re.search(r'&nbsp;<span class="score">\((.+?)\)</span>', javlib_html)
    if str(scoreg) != 'None':
        score = float(scoreg.group(1))
        score = (score - 4) * 5 / 3     # javlib上稍微有人关注的影片评分都是6分以上（10分制），强行把它差距拉大
        if score >= 0:
            score = '%.1f' % score
            nfo_dict['评分'] = str(score)
        else:
            nfo_dict['评分'] = '0'
    else:
        nfo_dict['评分'] = '0'
    # javlib的精彩影评   (.+?\s*.*?\s*.*?\s*.*?)  不用影片简介，用jaclib上的精彩影片，下面的匹配可能很奇怪，没办法，就这么奇怪
    review = re.findall(r'(hidden">.+?</textarea>)</td>\s*?<td class="scores"><table>\s*?<tr><td><span class="scoreup">\d\d+?</span>', javlib_html, re.DOTALL)
    plot_review = ''
    if len(review) != 0:
        plot_review = '\n【精彩影评】：'
        for rev in review:
            right_review = re.findall(r'hidden">(.+?)</textarea>', rev, re.DOTALL)
            if len(right_review) != 0:
                plot_review = plot_review + right_review[-1].replace('&', '和') + '////'
                continue
    #print(plot_review)
    #######################################################################
    # title = title.rstrip(nfo_dict['首个女优'])

    # arzon的简介
    plot = ''
    if if_nfo == '是' and if_plot == '是':
        while True:
            print('    >正在查找简介...')
            arzon_url = 'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q=' + nfo_dict['车牌']
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
                    fail_message = '    >连接arzon失败：' + arzon_url + '，可能是网络拥挤，也可能是成人验证失效！\n'
                    print(fail_message, end='')
                    plot = '【连接arzon失败！看到此提示请重新整理nfo！】'
                    break
            # arzon第一次搜索AV  <dt><a href="https://www.arzon.jp/item_1376110.html" title="限界集落に越してきた人妻 ～村民達の慰みモノにされる日々～"><img src=
            AVs = re.findall(r'<h2><a href="(/item.+?)" title=', search_html)
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
                            fail_message = '    >无法进入arzon的第一个搜索结果：' + av_url + ' \n'
                            print(fail_message, end='')
                            plot = '【连接arzon失败！看到此提示请重新整理nfo！】'
                            break
                    ############################################################################
                    plotg = re.search(r'<h2>作品紹介</h2>([\s\S]*?)</div>', first_html)
                    # 第一个页面找到plot
                    if str(plotg) != 'None':
                        plot_br = plotg.group(1)
                        plot = ''
                        for line in plot_br.split('<br />'):
                            line = line.strip().replace('＆', 'そして')
                            plot += line
                        plot = '【影片简介】：' + plot
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
                                    fail_message = '    >无法进入arzon第二个搜索结果：' + av_url + ' \n'
                                    print(fail_message, end='')
                                    plot = '【连接arzon失败！看到此提示请重新整理nfo！】'
                                    break
                            ############################################################################
                            plotg = re.search(r'<h2>作品紹介</h2>\s+?(.+?)\s{0,}<', second_html)
                            # 找到plot
                            if str(plotg) != 'None':
                                plot_br = plotg.group(1)
                                plot = ''
                                for line in plot_br.split('<br />'):
                                    line = line.strip().replace('＆', 'そして')
                                    plot += line
                                plot = '【影片简介】：' + plot
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
                                            fail_message = '    >无法进入arzon第三个搜索结果：' + av_url + ' \n'
                                            print(fail_message, end='')
                                            plot = '【连接arzon失败！看到此提示请重新整理nfo！】'
                                            break
                                    ############################################################################
                                    plotg = re.search(r'<h2>作品紹介</h2>\s+?(.+?)\s*<', third_html)
                                    # 找到plot
                                    if str(plotg) != 'None':
                                        plot_br = plotg.group(1)
                                        plot = ''
                                        for line in plot_br.split('<br />'):
                                            line = line.strip().replace('＆', 'そして')
                                            plot += line
                                        plot = '【影片简介】：' + plot
                                        break
                                    else:  # 第三个搜索界面也找不到
                                        fail_message = '    >arzon有三个搜索结果：' + arzon_url + '，但找不到简介！\n'
                                        print(fail_message, end='')
                                        plot = '【查无简介】'
                                        break
                                # 第三个页面不是/item_1441697.html
                                else:
                                    fail_message = '    >arzon有两个搜索结果：' + arzon_url + '，但找不到简介！\n'
                                    print(fail_message, end='')
                                    plot = '【查无简介】'
                                    break
                        else:
                            # 第二个页面不是/item_1441697.html
                            fail_message = '    >arzon有一个搜索结果：' + arzon_url + '，但找不到简介！\n'
                            print(fail_message, end='')
                            plot = '【查无简介】'
                            break
                # 第一个页面就不是/item_1441697.html，arzon搜索不到
                else:
                    fail_message = '    >arzon找不到该影片信息：' + arzon_url + '，可能被下架！\n'
                    print(fail_message, end='')
                    plot = '【影片下架，再无简介】'
                    break
            # arzon搜索页面实际是18岁验证
            else:
                adultg = re.search(r'１８歳未満', search_html)
                if str(adultg) != 'None':
                    fail_message = '    >arzon上出现成人验证，请重启程序！\n'
                    print(fail_message, end='')
                    plot = '【连接arzon失败！看到此提示请重新整理nfo！】'
                    os.system('pause')
                else:  # 不是成人验证，也没有结果
                    fail_message = '    >arzon的回复不是成人验证，也找不到影片：' + arzon_url + '\n'
                    print(fail_message, end='')
                    plot = '【影片下架，再无简介】'
                    break
        if if_tran == '是':
            plot = tran(ID, SK, plot, t_lang)
    # 企划 javlib上没有企划set
    new_mp4 = nfo_dict['车牌']
    if if_mp4 == '是':
        # 新文件名new_mp4
        new_mp4 = ''
        for j in rename_mp4_list:
            if j not in nfo_dict:
                new_mp4 = new_mp4 + j
            elif j != '全部女优':
                new_mp4 = new_mp4 + nfo_dict[j]
            else:
                new_mp4 = new_mp4 + ' '.join(nfo_dict[j])
        new_mp4 = new_mp4.rstrip(' ')

    if if_nfo == '是':
        # 写入nfo开始
        info_path = root + '\\' + new_mp4 + '.nfo'      #nfo存放的地址
        # 开始写入nfo，这nfo格式是参考的emby的nfo
        # try:
        f = open(info_path, 'w', encoding="utf-8")
        # except:
        #     print('    >保存失败：', info_path)
        #     continue
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n"
                "<movie>\n"
                "  <plot>" + plot + plot_review + "</plot>\n"
                "  <title>" + title + "</title>\n"
                "  <director>" + nfo_dict['导演'] + "</director>\n"
                "  <rating>" + nfo_dict['评分'] + "</rating>\n"
                "  <year>" + nfo_dict['发行年份'] + "</year>\n"
                "  <mpaa>NC-17</mpaa>\n"                            
                "  <customrating>NC-17</customrating>\n"
                "  <countrycode>JP</countrycode>\n"
                "  <premiered>" + nfo_dict['发行年月日'] + "</premiered>\n"
                "  <release>" + nfo_dict['发行年月日'] + "</release>\n"
                "  <runtime>" + nfo_dict['片长'] + "</runtime>\n"
                "  <country>日本</country>\n"
                "  <studio>" + nfo_dict['片商'] + "</studio>\n"
                "  <id>" + nfo_dict['车牌'] + "</id>\n"
                "  <num>" + nfo_dict['车牌'] + "</num>\n")
        for i in genres:
            f.write("  <genre>" + i + "</genre>\n")
        for i in genres:
            f.write("  <tag>" + i + "</tag>\n")
        for i in nfo_dict['全部女优']:
            f.write("  <actor>\n    <name>" + i + "</name>\n    <type>Actor</type>\n    <thumb></thumb>\n  </actor>\n")
        f.write("</movie>\n")
        f.close()
        print('    >nfo收集完成')

    #需要下载两张图片
    if if_jpg == '是':
        # 下载海报的地址 cover
        cover_url = 'http:' + cover
        # 默认的 全标题.jpg封面
        if if_qunhui != '是':
            fanart_path = root + '\\' + new_mp4 + '-fanart.jpg'
            poster_path = root + '\\' + new_mp4 + '-poster.jpg'
        else:
            fanart_path = root + '\\' + new_mp4 + '.jpg'
            poster_path = root + '\\' + new_mp4 + '.png'
        # 下载 海报
        try:
            print('    >正在下载封面：', cover_url)
            r = requests.get(cover_url, stream=True, timeout=10)
            with open(fanart_path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
            print('    >fanart.jpg下载成功')
        except:
            print('    >从javlibrary下载fanart.jpg失败，正在前往javbus...')
            # 在javbus上找信息
            bus_search_url = bus_url + nfo_dict['车牌']
            try:
                bus_search_rqs = requests.get(bus_search_url, timeout=10)
                bus_search_rqs.encoding = 'utf-8'
                bav_html = bus_search_rqs.text
            except:
                fail_message = '    >连接javbus失败：' + bus_search_url
                print(fail_message, end='')
                continue
            # DVD封面cover
            coverg = re.search(r'<a class="bigImage" href="(.+?)">', bav_html)  # 封面图片的正则对象
            if str(coverg) != 'None':
                cover_url = coverg.group(1)
                print('    >正在从javbus下载封面：', cover_url)
                try:
                    r = requests.get(cover_url, stream=True, timeout=10)
                    with open(fanart_path, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
                    print('    >fanart.jpg下载成功')
                except:
                    fail_message = '    >下载fanart.jpg失败：' + cover_url
                    print(fail_message, end='')
                    continue
            else:
                fail_message = '    >查找封面失败：' + bus_search_url
                print(fail_message, end='')
                continue
        try:
            img = Image.open(fanart_path)
            w, h = img.size  # fanart的宽
            ex = int(w * 0.52625)
            poster = img.crop((ex, 0, w, h))
            poster.save(poster_path, quality=95)
            print('    >poster.jpg裁剪成功')
        except:
            print('    >poster.jpg裁剪失败!')
        if if_qunhui == '是':
            shutil.copyfile(fanart_path, root + '\\Backdrop.jpg')

    # 收集女优头像
    if if_sculpture == '是':
        for each_actor in nfo_dict['全部女优']:
            exist_actor_path = '女优头像\\' + each_actor + '.jpg'
            # print(exist_actor_path)
            jpg_type = '.jpg'
            if not os.path.exists(exist_actor_path):  # 女优图片还没有
                exist_actor_path = '女优头像\\' + each_actor + '.png'
                if not os.path.exists(exist_actor_path):  # 女优图片还没有
                    fail_message = '    >没有女优头像：' + each_actor + '\n'
                    print(fail_message, end='')
                    config_actor = configparser.ConfigParser()
                    config_actor.read('【缺失的女优头像统计For Kodi】.ini')
                    try:
                        each_actor_times = config_actor.get('缺失的女优头像', each_actor)
                        config_actor.set("缺失的女优头像", each_actor, str(int(each_actor_times) + 1))
                    except:
                        config_actor.set("缺失的女优头像", each_actor, '1')
                    config_actor.write(open('【缺失的女优头像统计For Kodi】.ini', "w"))
                    continue
                else:
                    jpg_type = '.png'
            actors_path = root + '\\.actors\\'
            if not os.path.exists(actors_path):
                os.makedirs(actors_path)
            shutil.copyfile('女优头像\\' + each_actor + jpg_type,
                            actors_path + each_actor + jpg_type)
            print('    >女优头像收集完成：', each_actor)

    print()
