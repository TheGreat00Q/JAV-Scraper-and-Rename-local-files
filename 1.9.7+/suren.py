# -*- coding:utf-8 -*-
import requests, re, os, shutil, configparser, time, hashlib, json, traceback
from PIL import Image
from time import sleep
from tkinter import filedialog, Tk
from shutil import copyfile


# 功能为记录错误txt
def write_fail(fail_m):
    record_txt = open('【记得清理它】失败记录.txt', 'a', encoding="utf-8")
    record_txt.write(fail_m)
    record_txt.close()


# get_directory功能为获取用户选取的文件夹路径
def get_directory():
    directory_root = Tk()
    directory_root.withdraw()
    work_path = filedialog.askdirectory()
    if work_path == '':
        print('你没有选择目录! 请重新选：')
        sleep(2)
        # get_directory()
        return get_directory()
    else:
        # askdirectory 获得是 正斜杠 路径C:/，所以下面要把 / 换成 反斜杠\
        temp_path = work_path.replace('/', '\\')
        return temp_path


# 调用百度翻译API接口，返回中文简介str
def tran(api_id, key, word, to_lang):
    # init salt and final_sign
    salt = str(time.time())[:10]
    final_sign = api_id + word + salt + key
    final_sign = hashlib.md5(final_sign.encode("utf-8")).hexdigest()
    # 表单paramas
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


# 每一部jav的“结构体”
class JavFile(object):
    def __init__(self):
        self.name = 'ABC-123.mp4'  # 文件名
        self.car = 'ABC-123'  # 车牌
        self.episodes = 0     # 第几集


# 读取配置文件
print('1、须开启全局模式翻墙，访问jav321\n'
      '2、影片信息没有简介，没有导演，可能没有演员姓名，没有演员头像\n'
      '3、如有素人车牌识别不出，请在ini中添加该车牌\n')
config_settings = configparser.ConfigParser()
print('正在读取ini中的设置...', end='')

try:
    config_settings.read('ini的设置会影响所有exe的操作结果.ini')
    if_nfo = config_settings.get("收集nfo", "是否收集nfo？")
    if_exnfo = config_settings.get("收集nfo", "是否跳过已存在nfo的文件夹？")
    if_jpg = config_settings.get("获取两张jpg", "是否获取fanart.jpg和poster.jpg？")
    if_qunhui = config_settings.get("获取两张jpg", "是否采取群辉video station命名方式？")
    if_mp4 = config_settings.get("重命名影片", "是否重命名影片？")
    rename_mp4 = config_settings.get("重命名影片", "重命名影片的格式")
    if_folder = config_settings.get("修改文件夹", "是否重命名或创建独立文件夹？")
    rename_folder = config_settings.get("修改文件夹", "新文件夹的格式")
    simp_trad = config_settings.get("其他设置", "简繁中文？")
    suren_pref = config_settings.get("其他设置", "素人车牌(若有新车牌请自行添加)")
    file_type = config_settings.get("其他设置", "扫描文件类型")
    if_tran = config_settings.get("百度翻译API", "是否翻译为中文？")
    ID = config_settings.get("百度翻译API", "APP ID")
    SK = config_settings.get("百度翻译API", "密钥")
except:
    print('\nini文件无法读写，删除它，然后打开“【有码】基于javlibrary.exe”自动重新创建ini！')
    os.system('pause')
print('\n读取ini文件成功! ')

nfo_dict = {'空格': ' '}
suren_list = suren_pref.split('、')
rename_mp4_list = rename_mp4.split('+')    #重命名格式的列表，来自ini文件的rename_mp4
rename_folder_list = rename_folder.split('+')    #重命名格式的列表，来自ini文件的rename_floder
type_tuple = tuple(file_type.split('、'))   #重命名格式的列表，来自ini文件的rename_mp4
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}  # 伪装成浏览器浏览网页

if simp_trad == '简':  # https://tw.jav321.com/video/ssni00643
    url = 'https://www.jav321.com/search'
    t_lang = 'zh'
else:
    url = 'https://tw.jav321.com/search'
    t_lang = 'cht'

start_key = ''
while start_key == '':
    # 用户选择文件夹
    print('请选择要整理的文件夹：', end='')
    path = get_directory()
    print(path)
    write_fail('已选择文件夹：' + path + '\n')
    print('...文件扫描开始...如果时间过长...请避开中午夜晚高峰期...\n')
    fail_times = 0  # 处理过程中错失败的个数
    fail_list = []  # 用于存放处理失败的信息
    #【当前路径】 【子目录】 【文件】
    for root, dirs, files in os.walk(path):
        if if_exnfo == '是' and files and (files[-1].endswith('nfo') or (len(files) > 1 and files[-2].endswith('nfo'))):
            continue
        # 对这一层文件夹进行评估,有多少视频，有多少同车牌视频，是不是独立文件夹
        car_videos = []        # 存放：需要整理的jav的结构体
        cars_dic = {}         # 存放：每一部jav有几集？
        videos_num = 0        # 当前文件夹中视频的数量，可能有视频不是jav
        for raw_file in files:
            # 判断是不是视频，得到车牌号
            if raw_file.endswith(type_tuple):
                video_num_g = re.search(r'([a-zA-Z]{2,6})-? ?(\d{2,5})', raw_file)
                if str(video_num_g) != 'None':
                    num_pref = video_num_g.group(1)
                    num_pref = num_pref.upper()
                    if num_pref in suren_list:
                        num_suf = video_num_g.group(2)
                        car_num = num_pref + '-' + num_suf
                        video_type = '.' + str(raw_file.split('.')[-1])  # 文件类型的长度，如：mp4是3，rmvb是4
                        if car_num not in cars_dic:
                            cars_dic[car_num] = 1
                        else:
                            cars_dic[car_num] += 1
                        jav_file = JavFile()
                        jav_file.car = car_num
                        jav_file.name = raw_file
                        jav_file.episodes = cars_dic[car_num]
                        car_videos.append(jav_file)
                    else:
                        continue
                else:
                    continue
            else:
                continue
        if cars_dic:
            if len(cars_dic) > 1 or videos_num > len(car_videos) or len(dirs) > 1 or (
                    len(dirs) == 1 and dirs[0] != '.actors'):
                # 当前文件夹下， 车牌不止一个，还有其他非jav视频，有其他文件夹
                separate_folder = False
            else:
                separate_folder = True
        else:
            continue

        # 正式开始
        for srt in car_videos:
            try:
                car_num = srt.car
                file = srt.name
                # 获取nfo信息的jav321搜索网页
                params = {
                    'sn': car_num,
                }
                try:  # http://tw.jav321.com/
                    jav_html = requests.post(url, data=params, headers=headers, timeout=10).text
                except:
                    try:
                        jav_html = requests.post(url, data=params, headers=headers, timeout=10).text
                    except:
                        fail_times += 1
                        fail_message = '第' + str(fail_times) + '个失败！连接jav321失败：\\' + root.lstrip(path) + '\\' + file + '\n'
                        print('>>' + fail_message, end='')
                        fail_list.append('    >' + fail_message)
                        write_fail('    >' + fail_message)
                        continue
                # 尝试找标题
                titleg = re.search(r'<h3>(.+?) <small>', jav_html)  # 匹配处理“标题”
                # 搜索结果就是AV的页面
                if str(titleg) != 'None':
                    title = titleg.group(1)
                # 找不到标题，jav321找不到影片
                else:
                    fail_times += 1
                    fail_message = '第' + str(fail_times) + '个失败！找不到该车牌的影片：\\' + root.lstrip(path) + '\\' + file + '\n'
                    print('>>' + fail_message, end='')
                    fail_list.append('    >' + fail_message)
                    write_fail('    >' + fail_message)
                    continue

                # 素人的title开头不是车牌
                title = title.replace('\n', '').replace('&', '和').replace('\\', '#').replace('/', '#')\
                    .replace(':', '：').replace('*', '#').replace('?', '？').replace('"', '#').replace('<', '【')\
                    .replace('>', '】').replace('|', '#').replace('＜', '【').replace('＞', '】')
                # 处理标题过长
                if len(title) > 50:
                    title_easy = title[:50]
                else:
                    title_easy = title
                nfo_dict['标题'] = title_easy
                # 正则匹配 影片信息 开始
                # 车牌号
                nfo_dict['车牌'] = re.search(r'番.</b>: (.+?)<br>', jav_html).group(1).upper()
                # 上面匹配的title就是纯标题
                total_title = nfo_dict['车牌'] + ' ' + title
                print('>>正在处理：', total_title)
                # 片商</b>: <a href="/company/%E83%A0%28PRESTIGE+PREMIUM%29/1">プレステージプレミアム(PRESTIGE PREMIUM)</a>
                studiog = re.search(r'<a href="/company.+?">(.+?)</a>', jav_html)
                if str(studiog) != 'None':
                    nfo_dict['片商'] = studiog.group(1)
                else:
                    nfo_dict['片商'] = '未知片商'
                # 上映日 (\d\d\d\d-\d\d-\d\d)</td>
                premieredg = re.search(r'日期</b>: (\d\d\d\d-\d\d-\d\d)<br>', jav_html)
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
                runtimeg = re.search(r'播放..</b>: (\d+)', jav_html)
                if str(runtimeg) != 'None':
                    nfo_dict['片长'] = runtimeg.group(1)
                else:
                    nfo_dict['片长'] = '0'
                # 没有导演
                # 演员们 和 # 第一个演员   女优</b>: 花音さん 21歳 床屋さん(家族経営) &nbsp
                actorg = re.search(r'<small>(.+?)</small>', jav_html)
                if str(actorg) != 'None':
                    actor_str = actorg.group(1)
                    actor_list = actor_str.split(' ')
                    actor_list = [i for i in actor_list if i != '']
                    if len(actor_list) > 3:
                        nfo_dict['首个女优'] = actor_list[1] + ' ' + actor_list[2] + ' ' + actor_list[3]
                        nfo_dict['全部女优'] = [nfo_dict['首个女优']]
                    elif len(actor_list) > 1:
                        del actor_list[0]
                        nfo_dict['首个女优'] = ' '.join(actor_list)
                        print(nfo_dict['首个女优'])
                        nfo_dict['全部女优'] = [nfo_dict['首个女优']]
                    else:
                        nfo_dict['首个女优'] = '素人'
                        nfo_dict['全部女优'] = ['素人']
                else:
                    nfo_dict['首个女优'] = '素人'
                    nfo_dict['全部女优'] = ['素人']
                # 特点
                genres = re.findall(r'genre.+?">(.+?)</a>', jav_html)
                genres = [i for i in genres if i != '标签' and i != '標籤']
                if len(genres) == 0:
                    genres = ['无特点']
                if '-c.' in file or '-C.' in file:
                    genres.append('中文字幕')
                # 下载封面 cover fanart
                coverg = re.search(r'poster="(.+?)"><source', jav_html)  # 封面图片的正则对象
                if str(coverg) != 'None':
                    cover_url = coverg.group(1)
                else:  # src="http://pics.dmm.co.jp/digital/amateur/scute530/scute530jp-001.jpg"
                    coverg = re.search(r'img-responsive" src="(.+?)"', jav_html)  # 封面图片的正则对象
                    if str(coverg) != 'None':
                        cover_url = coverg.group(1)
                    else:  # src="http://pics.dmm.co.jp/digital/amateur/scute530/scute530jp-001.jpg"
                        coverg = re.search(r'src="(.+?)"', jav_html)  # 封面图片的正则对象
                        if str(coverg) != 'None':
                            cover_url = coverg.group(1)
                        else:
                            cover_url = ''
                # 下载海报 poster
                posterg = re.search(r'img-responsive" src="(.+?)"', jav_html)  # 封面图片的正则对象
                if str(posterg) != 'None':
                    poster_url = posterg.group(1)
                else:
                    poster_url = ''
                # 评分
                scoreg = re.search(r'评分</b>: (\d\.\d)<br>', jav_html)
                if str(scoreg) != 'None':
                    score = float(scoreg.group(1))
                    score = (score - 2) * 10 / 3
                    if score >= 0:
                        score = '%.1f' % score
                        nfo_dict['评分'] = str(score)
                    else:
                        nfo_dict['评分'] = '0'
                else:
                    scoreg = re.search(r'"/img/(\d\d)\.gif', jav_html)
                    if str(scoreg) != 'None':
                        score = float(scoreg.group(1))/10
                        score = (score - 2) * 10 / 3
                        if score >= 0:
                            score = '%.1f' % score
                            nfo_dict['评分'] = str(score)
                        else:
                            nfo_dict['评分'] = '0'
                    else:
                        nfo_dict['评分'] = '0'
                # 素人上没有企划set
                # 把标题当做plot
                plot = title
                if if_nfo == '是' and if_tran == '是':
                    print('    >正在日译中...')
                    plot = tran(ID, SK, title, t_lang)

                # 重命名视频
                new_mp4 = file.rstrip(video_type)
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
                    cd_msg = ''
                    if cars_dic[car_num] > 1:  # 是CD1还是CDn？
                        cd_msg = '-cd' + str(srt.episodes)
                        new_mp4 += cd_msg
                    try:
                        os.rename(root + '\\' + file, root + '\\' + new_mp4 + video_type)
                        file = new_mp4 + video_type
                        print('    >修改文件名' + cd_msg + '完成')
                    except:
                        fail_times += 1
                        fail_message = '    >第' + str(
                            fail_times) + '个失败！修改视频文件名失败，有多部同车牌视频，或者文件被后台打开了：\\' + root.lstrip(
                            path) + '\\' + file + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        write_fail(fail_message)

                # 重命名文件夹
                new_root = root
                if if_folder == '是':
                    # 新文件夹名rename_folder
                    new_folder = ''
                    for j in rename_folder_list:
                        if j not in nfo_dict:
                            new_folder = new_folder + j
                        elif j != '全部女优':
                            new_folder = new_folder + nfo_dict[j]
                        else:
                            new_folder = new_folder + ' '.join(nfo_dict[j])
                    new_folder = new_folder.rstrip(' ')
                    if separate_folder:
                        if cars_dic[car_num] == 1 or (
                                cars_dic[car_num] > 1 and cars_dic[car_num] == srt.episodes):  # 同一车牌有多部，且这是最后一部，才会重命名
                            newroot_list = root.split('\\')
                            del newroot_list[-1]
                            upper2_root = '\\'.join(newroot_list)
                            new_root = upper2_root + '\\' + new_folder  # 当前文件夹就会被重命名
                            # 修改文件夹
                            try:
                                os.rename(root, new_root)
                            except:
                                fail_times += 1
                                fail_message = '    >第' + str(
                                    fail_times) + '个失败！重命名文件夹名失败，内部文件被后台打开了，或者已经有同番号的文件夹了：\\' + root.lstrip(
                                    path) + '\\' + file + '\n'
                                print(fail_message, end='')
                                fail_list.append(fail_message)
                                write_fail(fail_message)
                                continue
                            print('    >重命名文件夹完成')
                    else:
                        if not os.path.exists(root + '\\' + new_folder):  # 已经存在目标文件夹
                            os.makedirs(root + '\\' + new_folder)
                        try:
                            os.rename(root + '\\' + file, root + '\\' + new_folder + '\\' + file)  # 就把影片放进去
                            new_root = root + '\\' + new_folder  # 在当前文件夹下再创建新文件夹
                            print('    >创建独立的文件夹完成')
                        except:
                            fail_times += 1
                            fail_message = '    >第' + str(
                                fail_times) + '个失败！创建独立的文件夹名失败，影片被后台打开了，或者已经有同番号的文件夹了：\\' + root.lstrip(
                                path) + '\\' + file + '\n'
                            print(fail_message, end='')
                            fail_list.append(fail_message)
                            write_fail(fail_message)
                            continue

                # 写入nfo
                if if_nfo:
                    # 写入nfo开始
                    info_path = new_root + '\\' + new_mp4 + '.nfo'
                    # 开始写入nfo
                    f = open(info_path, 'w', encoding="utf-8")
                    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n"
                            "<movie>\n"
                            "  <plot>" + plot + "</plot>\n"
                            "  <title>" + total_title + "</title>\n"
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
                        f.write(
                            "  <actor>\n    <name>" + i + "</name>\n    <type>Actor</type>\n  </actor>\n")
                    f.write("</movie>\n")
                    f.close()
                    print("    >nfo收集完成")

                # 需要两张图片
                if if_jpg == '是':
                    # 下载海报的地址 cover
                    print('    >fanart.jpg的链接：', cover_url)
                    # 默认的 全标题.jpg封面
                    if if_qunhui != '是':
                        fanart_path = new_root + '\\' + new_mp4 + '-fanart.jpg'
                        poster_path = new_root + '\\' + new_mp4 + '-poster.jpg'
                    else:
                        fanart_path = new_root + '\\' + new_mp4 + '.jpg'
                        poster_path = new_root + '\\' + new_mp4 + '.png'
                    # 下载 海报
                    try:
                        r = requests.get(cover_url, stream=True, timeout=10)
                        with open(fanart_path, 'wb') as f:
                            for chunk in r:
                                f.write(chunk)
                        print('    >fanart.jpg下载成功')
                    except:
                        fail_times += 1
                        fail_message = '    >第' + str(
                            fail_times) + '个失败！封面url：' + cover_url + '，网络不佳，下载失败：\\' + new_root.lstrip(path) + '\\' + file + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        write_fail(fail_message)
                        continue
                    # 下载poster.jpg   img-responsive" src="https://www.jav321.com/images/prestigepremium/300mium/034/pf_o1_300mium-034.jpg">
                    print('    >poster.jpg的链接：', poster_url)
                    try:
                        r = requests.get(poster_url, stream=True, timeout=10)
                        with open(poster_path, 'wb') as f:
                            for chunk in r:
                                f.write(chunk)
                        print('    >poster.jpg下载成功')
                    except:
                        fail_message = '    >下载poster.jpg封面失败：\\' + new_root.lstrip(path) + '\\' + file + '\n'
                        print(fail_message, end='')
                        write_fail(fail_message)
                        continue
                    if if_qunhui == '是':
                        shutil.copyfile(fanart_path, new_root + '\\Backdrop.jpg')

            except:
                print('如果多次看到以下信息，请截图给作者！')
                print(traceback.format_exc())
                fail_times += 1
                fail_message = '    >第' + str(fail_times) + '个失败！发生未知错误，如一直在该影片报错请联系作者：\\' + root.lstrip(
                    path) + '\\' + file + '\n'
                print(fail_message, end='')
                fail_list.append(fail_message)
                write_fail(fail_message)
                continue

    print('\n当前文件夹完成，', end='')
    if fail_times > 0:
        print('失败', fail_times, '个!  ', path, '\n')
        if len(fail_list) > 0:
            for fail in fail_list:
                print(fail, end='')
        print('\n“【记得清理它】失败记录.txt”已记录错误\n')
    else:
        print('没有处理失败的AV，干得漂亮！  ', path, '\n')

    start_key = input('回车继续选择文件夹整理：')