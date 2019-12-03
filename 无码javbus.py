# -*- coding:utf-8 -*-
import re, os, configparser, requests, shutil, traceback
from PIL import Image
from tkinter import filedialog, Tk
from time import sleep
from aip import AipBodyAnalysis


# get_directory功能是 获取用户选取的文件夹路径
def get_directory():
    directory_root = Tk()
    directory_root.withdraw()
    work_path = filedialog.askdirectory()
    if work_path == '':
        print('你没有选择目录! 请重新选：')
        sleep(2)
        return get_directory()
    else:
        # askdirectory 获得是 正斜杠 路径C:/，所以下面要把 / 换成 反斜杠\
        temp_path = work_path.replace('/', '\\')
        return temp_path


# 功能为记录错误txt
def write_fail(fail_m):
    record_txt = open('【记得清理它】失败记录.txt', 'a', encoding="utf-8")
    record_txt.write(fail_m)
    record_txt.close()


# 人体识别，返回鼻子位置
def image_cut(file_name, cli):
    with open(file_name, 'rb') as fp:
        image = fp.read()
    result = cli.bodyAnalysis(image)
    try:
        return int(result["person_info"][0]['body_parts']['nose']['x'])
    except:
        print('    >正在尝试重新人体检测...')
        return image_cut(file_name, cli)


# 每一部jav的“结构体”
class JavFile(object):
    def __init__(self):
        self.name = 'ABC-123.mp4'  # 文件名
        self.car = 'ABC-123'  # 车牌
        self.episodes = 0     # 第几集


#  main开始
print('1、如果连不上javbus，请更正防屏蔽地址\n'
      '2、无码影片没有简介\n'
      '3、找不到AV信息，请在javbus上确认，再修改本地视频文件名，如：\n'
      '   112314-742-carib-1080p.mp4 => 112314-742.mp4\n'
      '   Heyzo_HD_0733_full.mp4 => Heyzo_0733.mp4\n')
# 读取配置文件，这个ini文件用来给用户设置重命名的格式和jav网址
config_settings = configparser.RawConfigParser()
print('正在读取ini中的设置...', end='')
try:
    config_settings.read('ini的设置会影响所有exe的操作结果.ini')
    if_nfo = config_settings.get("收集nfo", "是否收集nfo？")
    if_exnfo = config_settings.get("收集nfo", "是否跳过已存在nfo的文件夹？")
    if_mp4 = config_settings.get("重命名影片", "是否重命名影片？")
    rename_mp4 = config_settings.get("重命名影片", "重命名影片的格式")
    if_floder = config_settings.get("修改文件夹", "是否重命名或创建独立文件夹？")
    rename_folder = config_settings.get("修改文件夹", "新文件夹的格式")
    if_jpg = config_settings.get("获取两张jpg", "是否获取fanart.jpg和poster.jpg？")
    if_qunhui = config_settings.get("获取两张jpg", "是否采取群辉video station命名方式？")
    if_sculpture = config_settings.get("kodi专用", "是否收集女优头像")
    simp_trad = config_settings.get("其他设置", "简繁中文？")
    bus_url = config_settings.get("其他设置", "javbus网址")
    suren_pref = config_settings.get("其他设置", "素人车牌(若有新车牌请自行添加)")
    file_type = config_settings.get("其他设置", "扫描文件类型")
    if_face = config_settings.get("百度人体检测", "是否需要准确定位人脸的poster？")
    appid = config_settings.get("百度人体检测", "AppID")
    apikey = config_settings.get("百度人体检测", "API Key")
    sk = config_settings.get("百度人体检测", "Secret Key")
except:
    print('\n这个ini文件无法读写，删除它，然后打开“【有码】基于javlibrary.exe”自动重新创建ini！')
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
print('\n读取ini文件成功!')

if if_face == '是':
    client = AipBodyAnalysis(appid, apikey, sk)
nfo_dict = {'空格': ' '}                   # 用于暂时存放影片信息，女优，标题等
suren_list = suren_pref.split('、')        # 素人番号的列表，来自ini文件的suren_pref
rename_mp4_list = rename_mp4.split('+')    # 重命名视频的格式，来自ini文件的rename_mp4
rename_folder_list = rename_folder.split('+')    # 重命名文件夹的格式，来自ini文件的rename_floder
type_tuple = tuple(file_type.split('、'))   # 视频文件的类型，来自ini文件的file_type
gen_dict = {'无特点': '无特点', '高清': 'XXXX', '字幕': 'XXXX', '推薦作品': '推荐作品', '通姦': '通奸', '淋浴': '淋浴', '舌頭': '舌头', '下流': '下流',
            '敏感': '敏感', '變態': '变态', '願望': '愿望', '慾求不滿': '慾求不满', '服侍': '服侍', '外遇': '外遇', '訪問': '访问',
            '性伴侶': '性伴侣', '保守': '保守', '購物': '购物', '誘惑': '诱惑', '出差': '出差', '煩惱': '烦恼', '主動': '主动',
            '再會': '再会', '戀物癖': '恋物癖', '問題': '问题', '騙奸': '骗奸', '鬼混': '鬼混', '高手': '高手', '順從': '顺从',
            '密會': '密会', '做家務': '做家务', '秘密': '秘密', '送貨上門': '送货上门', '壓力': '压力', '處女作': '处女作',
            '淫語': '淫语', '問卷': '问卷', '住一宿': '住一宿', '眼淚': '眼泪', '跪求': '跪求', '求職': '求职', '婚禮': '婚礼',
            '第一視角': '第一视角', '洗澡': '洗澡', '首次': '首次', '劇情': '剧情', '約會': '约会', '實拍': '实拍', '同性戀': '同性恋',
            '幻想': '幻想', '淫蕩': '淫荡', '旅行': '旅行', '面試': '面试', '喝酒': '喝酒', '尖叫': '尖叫', '新年': '新年',
            '借款': '借款', '不忠': '不忠', '檢查': '检查', '羞恥': '羞耻', '勾引': '勾引', '新人': '新人', '推銷': '推销',
            'ブルマ': '运动短裤', 'AV女優': 'AV女优', '情人': '情人', '丈夫': '丈夫', '辣妹': '辣妹', 'S級女優': 'S级女优',
            '白領': '白领', '偶像': '偶像', '兒子': '儿子', '女僕': '女仆', '老師': '老师', '夫婦': '夫妇', '保健室': '保健室',
            '朋友': '朋友', '工作人員': '工作人员', '明星': '明星', '同事': '同事', '面具男': '面具男', '上司': '上司',
            '睡眠系': '睡眠系', '奶奶': '奶奶', '播音員': '播音员', '鄰居': '邻居', '親人': '亲人', '店員': '店员',
            '魔女': '魔女', '視訊小姐': '视讯小姐', '大學生': '大学生', '寡婦': '寡妇', '小姐': '小姐', '秘書': '秘书',
            '人妖': '人妖', '啦啦隊': '啦啦队', '美容師': '美容师', '岳母': '岳母', '警察': '警察', '熟女': '熟女',
            '素人': '素人', '人妻': '人妻', '痴女': '痴女', '角色扮演': '角色扮演', '蘿莉': '萝莉', '姐姐': '姐姐',
            '模特': '模特', '教師': '教师', '學生': '学生', '少女': '少女', '新手': '新手', '男友': '男友', '護士': '护士',
            '媽媽': '妈妈', '主婦': '主妇', '孕婦': '孕妇', '女教師': '女教师', '年輕人妻': '年轻人妻', '職員': '职员',
            '看護': '看护', '外觀相似': '外观相似', '色狼': '色狼', '醫生': '医生', '新婚': '新婚', '黑人': '黑人',
            '空中小姐': '空中小姐', '運動系': '运动系', '女王': '女王', '西裝': '西装', '旗袍': '旗袍', '兔女郎': '兔女郎',
            '白人': '白人', '制服': '制服', '內衣': '内衣', '休閒裝': '休閒装', '水手服': '水手服', '全裸': '全裸',
            '不穿內褲': '不穿内裤', '和服': '和服', '不戴胸罩': '不戴胸罩', '連衣裙': '连衣裙', '打底褲': '打底裤',
            '緊身衣': '紧身衣', '客人': '客人', '晚禮服': '晚礼服', '治癒系': '治癒系', '大衣': '大衣', '裸體襪子': '裸体袜子',
            '絲帶': '丝带', '睡衣': '睡衣', '面具': '面具', '牛仔褲': '牛仔裤', '喪服': '丧服', '極小比基尼': '极小比基尼',
            '混血': '混血', '毛衣': '毛衣', '頸鏈': '颈链', '短褲': '短裤', '美人': '美人', '連褲襪': '连裤袜', '裙子': '裙子',
            '浴衣和服': '浴衣和服', '泳衣': '泳衣', '網襪': '网袜', '眼罩': '眼罩', '圍裙': '围裙', '比基尼': '比基尼',
            '情趣內衣': '情趣内衣', '迷你裙': '迷你裙', '套裝': '套装', '眼鏡': '眼镜', '丁字褲': '丁字裤', '陽具腰帶':
                '阳具腰带', '男装': '男装', '襪': '袜', '美肌': '美肌', '屁股': '屁股', '美穴': '美穴', '黑髮': '黑发',
            '嬌小': '娇小', '曬痕': '晒痕', 'F罩杯': 'F罩杯', 'E罩杯': 'E罩杯', 'D罩杯': 'D罩杯', '素顏': '素颜',
            '貓眼': '猫眼', '捲髮': '捲发', '虎牙': '虎牙', 'C罩杯': 'C罩杯', 'I罩杯': 'I罩杯', '小麥色': '小麦色',
            '大陰蒂': '大阴蒂', '美乳': '美乳', '巨乳': '巨乳', '豐滿': '丰满', '苗條': '苗条', '美臀': '美臀', '美腿': '美腿',
            '無毛': '无毛', '美白': '美白', '微乳': '微乳', '性感': '性感', '高個子': '高个子', '爆乳': '爆乳', 'G罩杯': 'G罩杯',
            '多毛': '多毛', '巨臀': '巨臀', '軟體': '软体', '巨大陽具': '巨大阳具', '長發': '长发', 'H罩杯': 'H罩杯',
            '舔陰': '舔阴', '電動陽具': '电动阳具', '淫亂': '淫乱', '射在外陰': '射在外阴', '猛烈': '猛烈', '後入內射': '后入内射',
            '足交': '足交', '射在胸部': '射在胸部', '側位內射': '侧位内射', '射在腹部': '射在腹部', '騎乘內射': '骑乘内射',
            '射在頭髮': '射在头发', '母乳': '母乳', '站立姿勢': '站立姿势', '肛射': '肛射', '陰道擴張': '阴道扩张',
            '內射觀察': '内射观察', '射在大腿': '射在大腿', '精液流出': '精液流出', '射在屁股': '射在屁股', '內射潮吹': '内射潮吹',
            '首次肛交': '首次肛交', '射在衣服上': '射在衣服上', '首次內射': '首次内射', '早洩': '早洩', '翻白眼': '翻白眼',
            '舔腳': '舔脚', '喝尿': '喝尿', '口交': '口交', '內射': '内射', '自慰': '自慰', '後入': '后入', '騎乘位': '骑乘位',
            '顏射': '颜射', '口內射精': '口内射精', '手淫': '手淫', '潮吹': '潮吹', '輪姦': '轮奸', '亂交': '乱交', '乳交': '乳交',
            '小便': '小便', '吸精': '吸精', '深膚色': '深肤色', '指法': '指法', '騎在臉上': '骑在脸上', '連續內射': '连续内射',
            '打樁機': '打桩机', '肛交': '肛交', '吞精': '吞精', '鴨嘴': '鸭嘴', '打飛機': '打飞机', '剃毛': '剃毛',
            '站立位': '站立位', '高潮': '高潮', '二穴同入': '二穴同入', '舔肛': '舔肛', '多人口交': '多人口交', '痙攣':
                '痉挛', '玩弄肛門': '玩弄肛门', '立即口交': '立即口交', '舔蛋蛋': '舔蛋蛋', '口射': '口射', '陰屁': '阴屁',
            '失禁': '失禁', '大量潮吹': '大量潮吹', '69': '69', '振動': '振动', '搭訕': '搭讪', '奴役': '奴役',
            '打屁股': '打屁股', '潤滑油': '润滑油', '按摩': '按摩', '散步': '散步', '扯破連褲襪': '扯破连裤袜', '手銬': '手铐',
            '束縛': '束缚', '調教': '调教', '假陽具': '假阳具', '變態遊戲': '变态游戏', '注視': '注视', '蠟燭': '蜡烛',
            '電鑽': '电钻', '亂搞': '乱搞', '摩擦': '摩擦', '項圈': '项圈', '繩子': '绳子', '灌腸': '灌肠', '監禁': '监禁',
            '車震': '车震', '鞭打': '鞭打', '懸掛': '悬挂', '喝口水': '喝口水', '精液塗抹': '精液涂抹', '舔耳朵': '舔耳朵',
            '女體盛': '女体盛', '便利店': '便利店', '插兩根': '插两根', '開口器': '开口器', '暴露': '暴露',
            '陰道放入食物': '阴道放入食物', '大便': '大便', '經期': '经期', '惡作劇': '恶作剧', '電動按摩器': '电动按摩器',
            '凌辱': '凌辱', '玩具': '玩具', '露出': '露出', '肛門': '肛门', '拘束': '拘束', '多P': '多P', '潤滑劑': '润滑剂',
            '攝影': '摄影', '野外': '野外', '陰道觀察': '阴道观察', 'SM': 'SM', '灌入精液': '灌入精液', '受虐': '受虐',
            '綁縛': '绑缚', '偷拍': '偷拍', '異物插入': '异物插入', '電話': '电话', '公寓': '公寓', '遠程操作': '远程操作',
            '偷窺': '偷窥', '踩踏': '踩踏', '無套': '无套', '企劃物': '企划物', '獨佔動畫': '独佔动画', '10代': '10代',
            '1080p': 'XXXX', '人氣系列': '人气系列', '60fps': 'XXXX', '超VIP': '超VIP', '投稿': '投稿', 'VIP': 'VIP',
            '椅子': '椅子', '風格出眾': '风格出众', '首次作品': '首次作品', '更衣室': '更衣室', '下午': '下午', 'KTV': 'KTV',
            '白天': '白天', '最佳合集': '最佳合集', 'VR': 'VR', '動漫': '动漫', '酒店': '酒店', '密室': '密室', '車': '车',
            '床': '床', '陽台': '阳台', '公園': '公园', '家中': '家中', '公交車': '公交车', '公司': '公司', '門口': '门口',
            '附近': '附近', '學校': '学校', '辦公室': '办公室', '樓梯': '楼梯', '住宅': '住宅', '公共廁所': '公共厕所',
            '旅館': '旅馆', '教室': '教室', '廚房': '厨房', '桌子': '桌子', '大街': '大街', '農村': '农村', '和室': '和室',
            '地下室': '地下室', '牢籠': '牢笼', '屋頂': '屋顶', '游泳池': '游泳池', '電梯': '电梯', '拍攝現場': '拍摄现场',
            '別墅': '别墅', '房間': '房间', '愛情旅館': '爱情旅馆', '車內': '车内', '沙發': '沙发', '浴室': '浴室',
            '廁所': '厕所', '溫泉': '温泉', '醫院': '医院', '榻榻米': '榻榻米', '折磨': '折磨', '嘔吐': '呕吐', '觸手': '触手',
            '蠻橫嬌羞': '蛮横娇羞', '處男': '处男', '正太控': '正太控', '出軌': '出轨', '瘙癢': '瘙痒', '運動': '运动',
            '女同接吻': '女同接吻', '性感的': '性感的', '美容院': '美容院', '處女': '处女', '爛醉如泥的': '烂醉如泥的',
            '殘忍畫面': '残忍画面', '妄想': '妄想', '學校作品': '学校作品', '粗暴': '粗暴',
            '姐妹': '姐妹', '雙性人': '双性人', '跳舞': '跳舞', '性奴': '性奴', '倒追': '倒追', '性騷擾': '性骚扰', '其他': '其他',
            '戀腿癖': '恋腿癖', '偷窥': '偷窥', '花癡': '花癡', '男同性恋': '男同性恋', '情侶': '情侣', '戀乳癖': '恋乳癖',
            '亂倫': '乱伦', '其他戀物癖': '其他恋物癖', '偶像藝人': '偶像艺人', '野外・露出': '野外・露出', '獵豔': '猎豔',
            '女同性戀': '女同性恋', '企畫': '企画', '10枚組': '10枚组', '科幻': '科幻',
            '女優ベスト・総集編': '女演员的总编', '温泉': '温泉', 'M男': 'M男', '原作コラボ': '原作协作',
            '16時間以上作品': '16时间以上作品', 'デカチン・巨根': '巨根', 'ファン感謝・訪問': '感恩祭',
            '動画': '动画', '巨尻': '巨尻', 'ハーレム': '后宫', '日焼け': '晒黑', '早漏': '早漏', 'キス・接吻': '接吻.',
            '汗だく': '汗流浃背', 'スマホ専用縦動画': '相关视频', 'Vシネマ': '电影放映', 'Don Cipote\'s choice': 'Don Cipote\'s choice',
            'アニメ': '日本动漫', 'アクション': 'アクション', '动作': 'イメージビデオ（男性）',
            '孕ませ': '孕育吧', 'ビッチ': 'ビッチ', '特典あり（AVベースボール）': '有优惠（AV棒球）',
            'コミック雑誌': 'コミック雑志', '時間停止': '时间停止', '黑幫成員': '黑帮成员', '童年朋友': '童年朋友', '公主': '公主',
            '亞洲女演員': '亚洲女演员', '伴侶': '伴侣', '講師': '讲师', '婆婆': '婆婆', '女檢察官': '女检察官',
            '明星臉': '明星脸', '女主人、女老板': '女主人、女老板', '模特兒': '模特儿', '美少女': '美少女',
            '新娘、年輕妻子': '新娘、年轻妻子', '格鬥家': '格斗家', '車掌小姐': '车掌小姐',
            '千金小姐': '千金小姐', '已婚婦女': '已婚妇女', '女醫生': '女医生', '各種職業': '各种职业',
            '妓女': '妓女', '賽車女郎': '赛车女郎', '女大學生': '女大学生', '展場女孩': '展场女孩',
            '母親': '母亲', '家教': '家教', '护士': '护士', '蕩婦': '荡妇', '黑人演員': '黑人演员', '女生': '女生',
            '女主播': '女主播', '高中女生': '高中女生', '服務生': '服务生', '魔法少女': '魔法少女', '學生（其他）': '学生（其他）',
            '動畫人物': '动画人物', '遊戲的真人版': '游戏的真人版', '超級女英雄': '超级女英雄',
            '女戰士': '女战士', '及膝襪': '及膝袜', '娃娃': '娃娃', '女忍者': '女忍者', '女裝人妖': '女装人妖',
            '猥褻穿著': '猥亵穿着', '貓耳女': '猫耳女', '女祭司': '女祭司', '泡泡襪': '泡泡袜',
            '裸體圍裙': '裸体围裙', '迷你裙警察': '迷你裙警察',
            '身體意識': '身体意识', 'OL': 'OL', '和服・喪服': '和服・丧服', '體育服': '体育服',
            '學校泳裝': '学校泳装', '女傭': '女佣',
            '校服': '校服', '泳裝': '泳装', '哥德蘿莉': '哥德萝莉', '和服・浴衣':
                '和服・浴衣', '超乳': '超乳', '肌肉': '肌肉', '乳房': '乳房', '嬌小的': '娇小的', '高': '高',
            '變性者': '变性者', '胖女人': '胖女人', '成熟的女人': '成熟的女人',
            '蘿莉塔': '萝莉塔', '貧乳・微乳': '贫乳・微乳', '顏面騎乘': '颜面骑乘', '食糞': '食粪',
            '手指插入': '手指插入', '女上位': '女上位', '拳交': '拳交',
            '深喉': '深喉', '排便': '排便', '飲尿': '饮尿',
            '濫交': '滥交', '放尿': '放尿', '打手槍': '打手枪',
            '中出': '中出', '肛内中出': '肛内中出', '女優按摩棒': '女优按摩棒',
            '子宮頸': '子宫颈', '催眠': '催眠', '乳液': '乳液',
            '插入異物': '插入异物', '紧缚': '紧缚', '強姦': '强奸', '藥物': '药物',
            '汽車性愛': '汽车性爱', '糞便': '粪便', '跳蛋': '跳蛋', '緊縛': '紧缚', '按摩棒': '按摩棒',
            '性愛': '性爱', '逆強姦': '逆强奸', '合作作品': '合作作品', '恐怖': '恐怖',
            '給女性觀眾': '给女性观众', '教學': '教学', 'DMM專屬': 'DMM专属', 'R-15': 'R-15', 'R-18': 'R-18',
            '3D': '3D', '特效': '特效', '故事集': '故事集', '限時降價': '限时降价', '複刻版': '复刻版', '戀愛': '恋爱',
            '高畫質': '高画质', '主觀視角': '主观视角', '介紹影片': '介绍影片', '4小時以上作品': '4小时以上作品', '薄馬賽克': '薄马赛克',
            '經典': '经典', '首次亮相': '首次亮相', '數位馬賽克': '数位马赛克', '纪录片': '纪录片',
            '國外進口': '国外进口', '第一人稱攝影': '第一人称摄影', '業餘': '业馀', '局部特寫': '局部特写', '獨立製作': '独立制作',
            'DMM獨家': 'DMM独家', '單體作品': '单体作品', '合集': '合集', '天堂TV': '天堂TV',
            'DVD多士爐': 'DVD多士炉', 'AV OPEN 2014 スーパーヘビー': 'AV OPEN 2014超级重型',
            'AV OPEN 2014 ヘビー級': 'AV OPEN 2014重量级', 'AV OPEN 2014 ミドル級': 'AV OPEN 2014中量级',
            'AV OPEN 2015 マニア/フェチ部門': 'AV OPEN 2015 マニア/フェチ部门', 'AV OPEN 2015 熟女部門': 'AV OPEN 2015 熟女部门',
            'AV OPEN 2015 企画部門': 'AV OPEN 2015 企画部门', 'AV OPEN 2015 乙女部門': 'AV OPEN 2015 少女部',
            'AV OPEN 2015 素人部門': 'AV OPEN 2015 素人部门', 'AV OPEN 2015 SM/ハード部門': 'AV OPEN 2015 SM /硬件',
            'AV OPEN 2015 女優部門': 'AV OPEN 2015 女优部门', 'AVOPEN2016人妻・熟女部門': 'AVOPEN2016人妻・熟女部门',
            'AVOPEN2016企画部門': 'AVOPEN2016企画部', 'AVOPEN2016ハード部門': 'AVOPEN2016ハード部',
            'AVOPEN2016マニア・フェチ部門': 'AVOPEN2016疯狂恋物科', 'AVOPEN2016乙女部門': 'AVOPEN2016少女部',
            'AVOPEN2016女優部門': 'AVOPEN2016女优部', 'AVOPEN2016ドラマ・ドキュメンタリー部門': 'AVOPEN2016电视剧纪录部',
            'AVOPEN2016素人部門': 'AVOPEN2016素人部', 'AVOPEN2016バラエティ部門': 'AVOPEN2016娱乐部',
            'VR専用': 'VR専用', '堵嘴·喜劇': '堵嘴·喜剧', '性別轉型·女性化': '性别转型·女性化',
            '為智能手機推薦垂直視頻': '为智能手机推荐垂直视频', '設置項目': '设置项目', '迷你係列': '迷你系列',
            '體驗懺悔': '体验忏悔', '黑暗系統': '黑暗系统', 'オナサポ': '手淫', 'アスリート': '运动员',
            '覆面・マスク': '蒙面具', 'ハイクオリティVR': '高品质VR', 'ヘルス・ソープ': '保健香皂',
            'ホテル': '旅馆', 'アクメ・オーガズム': '绝顶高潮', '花嫁': '花嫁', 'デート': '约会',
            '軟体': '软体', '娘・養女': '养女', 'スパンキング': '打屁股', 'スワッピング・夫婦交換': '夫妇交换',
            '部下・同僚': '部下・同僚', '胸チラ': '露胸', 'バック': '后卫', 'エロス': '爱的欲望',
            '男の潮吹き': '男人高潮', '女上司': '女上司', 'セクシー': '性感美女', '受付嬢': '接待小姐', 'ノーブラ': '不穿胸罩',
            '白目・失神': '白眼失神', 'M女': 'M女', '女王様': '女王大人', 'ノーパン': '不穿内裤', 'セレブ': '名流',
            '病院・クリニック': '医院诊所', '面接': '面试', 'お風呂': '浴室', '叔母さん': '叔母阿姨', '罵倒': '骂倒',
            'お爺ちゃん': '爷爷', '逆レイプ': '强奸小姨子', 'ディルド': 'ディルド', 'ヨガ': '瑜伽',
            '飲み会・合コン': '酒会、联谊会', '部活・マネージャー': '社团经理', 'お婆ちゃん': '外婆',
            'ビジネススーツ': '商务套装', 'チアガール': '啦啦队女孩', 'ママ友': '妈妈的朋友', 'エマニエル': '片商Emanieru熟女塾',
            '妄想族': '妄想族', '蝋燭': '蜡烛', '鼻フック': '鼻钩儿', }                   # 特点

start_key = ''
while start_key == '':
    # 用户选择文件夹
    print('请选择要整理的文件夹：', end='')
    path = get_directory()
    print(path)
    write_fail('已选择文件夹：' + path+'\n')
    print('...文件扫描开始...如果时间过长...请避开中午夜晚高峰期...\n')
    fail_times = 0                             # 处理过程中错失败的个数
    fail_list = []                             # 用于存放处理失败的信息

    # root【当前根目录】 dirs【子目录】 files【文件】，root是字符串，后两个是列表
    for root, dirs, files in os.walk(path):
        if if_exnfo == '是' and files and (files[-1].endswith('nfo') or (len(files) > 1 and files[-2].endswith('nfo'))):
            continue
        # 对这一层文件夹进行评估,有多少视频，有多少同车牌视频，是不是独立文件夹
        car_videos = []  # 存放：需要整理的jav的结构体
        cars_dic = {}  # 存放：每一部jav有几集？
        videos_num = 0  # 当前文件夹中视频的数量，可能有视频不是jav
        for raw_file in files:
            # try:
            # 判断是不是视频，得到车牌号
            if raw_file.endswith(type_tuple):  # ([a-zA-Z]*\d*-?)+
                videos_num += 1
                video_num_g = re.search(r'([a-zA-Z0-9]+-?_?[a-zA-Z0-9]+-?_?\d*)', raw_file)
                if str(video_num_g) != 'None':  # 如果你下过上千部片，各种参差不齐的命名，你就会理解我了。
                    car_num = video_num_g.group(1)
                    alpg = re.search(r'([a-zA-Z]+)', car_num)
                    if str(alpg) != 'None':
                        if alpg.group(1).upper() in suren_list:  # 如果这是素人影片，告诉一下用户，它们需要另外处理
                            fail_times += 1
                            fail_message = '第' + str(fail_times) + '个警告！素人影片：\\' + root.lstrip(path) + '\\' + raw_file + '\n'
                            print('>>' + fail_message, end='')
                            fail_list.append('    >' + fail_message)
                            write_fail('    >' + fail_message)
                            continue
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

        if cars_dic:
            if len(cars_dic) > 1 or videos_num > len(car_videos) or len(dirs) > 1 or (
                    len(dirs) == 1 and dirs[0] != '.actors'):
                # 当前文件夹下， 车牌不止一个，还有其他非jav视频，有其他文件夹
                separate_folder = False
            else:
                separate_folder = True
        else:
            continue

        # print(car_videos)
        # 正式开始
        for srt in car_videos:
            try:
                car_num = srt.car
                file = srt.name
                # 获取nfo信息的javbus搜索网页
                search_url = bus_url + 'uncensored/search/' + car_num + '&type=&parent=uc'
                try:
                    jav_rqs = requests.get(search_url, timeout=10)
                    jav_rqs.encoding = 'utf-8'
                    jav_html = jav_rqs.text
                except:
                    fail_times += 1
                    fail_message = '    >第' + str(fail_times) + '个失败！连接javbus失败：' + search_url + '，\\' + root.lstrip(
                        path) + '\\' + file + '\n'
                    print(fail_message, end='')
                    fail_list.append(fail_message)
                    write_fail(fail_message)
                    continue
                # 搜索结果的网页，大部分情况一个结果，也有可能是多个结果的网页 <a class="movie-box" href="https://www.cdnbus.work/030619-872">
                # 尝试找movie-box，第一种情况：找得到，就是这个影片的网页
                bav_urls = re.findall(r'<a class="movie-box" href="(.+?)">', jav_html)  # 匹配处理“标题”
                # 搜索结果就是AV的页面
                if len(bav_urls) == 1:
                    bav_url = bav_urls[0]
                elif len(bav_urls) > 1:  # 找到不止一个
                    print('>>该车牌：' + car_num + ' 搜索到多个结果，正在尝试精确定位...')
                    car_suf = re.findall(r'\d+', car_num)[-1]  # 匹配处理“01”
                    car_suf = car_suf.lstrip('0')
                    car_prefs = re.findall(r'[a-zA-Z]+', car_num)  # 匹配处理“n”
                    if car_prefs:
                        car_pref = car_prefs[-1].upper()
                        # print(car_pref)
                    else:
                        car_pref = ''
                    bav_url = ''
                    for i in bav_urls:
                        # print(re.findall(r'\d+', i.split('/')[-1]))
                        url_suf = re.findall(r'\d+', i.split('/')[-1])[-1]  # 匹配处理“01”
                        url_suf = url_suf.lstrip('0')
                        if car_suf == url_suf:  # 数字相同
                            url_prefs = re.findall(r'[a-zA-Z]+', i.split('/')[-1])  # 匹配处理“n”
                            if url_prefs:
                                url_pref = url_prefs[-1].upper()
                                # print(url_pref)
                            else:
                                url_pref = ''
                            if car_pref == url_pref:  # 字母相同
                                bav_url = i
                                fail_times += 1
                                fail_message = '第' + str(fail_times) + '个警告！从“' + file + '”的多个搜索结果中确定为：' + bav_url + '\n'
                                print('>>' + fail_message, end='')
                                fail_list.append('    >' + fail_message)
                                write_fail('    >' + fail_message)
                                break
                        else:
                            continue
                    # 没找到，还是空
                    if bav_url == '':
                        fail_times += 1
                        fail_message = '第' + str(fail_times) + '个失败！找不到AV信息：' + search_url + '，\\' + root.lstrip(
                            path) + '\\' + file + '\n'
                        print('>>' + fail_message, end='')
                        fail_list.append('    >' + fail_message)
                        write_fail('    >' + fail_message)
                        continue
                else:  # 无码找不到
                    # 获取nfo信息的javbus搜索网页
                    search_url = bus_url + 'search/' + car_num + '&type=1'
                    try:
                        jav_rqs = requests.get(search_url, timeout=10)
                        jav_rqs.encoding = 'utf-8'
                        jav_html = jav_rqs.text
                    except:
                        fail_times += 1
                        fail_message = '    >第' + str(fail_times) + '个失败！连接javbus失败：' + search_url + '，\\' + root.lstrip(
                            path) + '\\' + file + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        write_fail(fail_message)
                        continue
                    bav_urls = re.findall(r'<a class="movie-box" href="(.+?)">', jav_html)  # 匹配处理“标题”
                    if len(bav_urls) > 0:
                        print('>>跳过有码影片：', file)
                        continue
                    fail_times += 1
                    fail_message = '第' + str(fail_times) + '个失败！找不到AV信息：' + search_url + '，\\' + root.lstrip(
                        path) + '\\' + file + '\n'
                    print('>>' + fail_message, end='')
                    fail_list.append('    >' + fail_message)
                    write_fail('    >' + fail_message)
                    continue
                try:
                    bav_rqs = requests.get(bav_url, timeout=10)
                    bav_rqs.encoding = 'utf-8'
                    bav_html = bav_rqs.text
                except:
                    fail_times += 1
                    fail_message = '    >第' + str(fail_times) + '个失败！打开javbus的搜索页面失败：' + search_url + '，\\' + root.lstrip(
                        path) + '\\' + file + '\n'
                    print(fail_message, end='')
                    fail_list.append(fail_message)
                    write_fail(fail_message)
                    continue

                # 正则匹配 影片信息 开始！
                # title的开头是车牌号，而我想要后面的纯标题
                try:
                    title = re.search(r'<title>(.+?) - JavBus</title>', bav_html, re.DOTALL).group(1)   # 这边匹配番号
                except:
                    fail_times += 1
                    fail_message = '第' + str(fail_times) + '个失败！页面上找不到AV信息：' + bav_url + '，\\' + root.lstrip(
                        path) + '\\' + file + '\n'
                    print('>>' + fail_message, end='')
                    fail_list.append('    >' + fail_message)
                    write_fail('    >' + fail_message)
                    continue

                # 去除title中的特殊字符
                title = title.replace('&', '和').replace('\\', '#').replace('/', '#').replace(':', '：') \
                    .replace('*', '#').replace('?', '？').replace('"', '#').replace('<', '【').replace('>', '】') \
                    .replace('|', '#').replace('＜', '【').replace('＞', '】')
                # 处理影片的标题过长
                if len(title) > 50:
                    title_easy = title[:50]
                else:
                    title_easy = title
                nfo_dict['标题'] = title_easy.split(' ', 1)[1]
                # <title>030619-872 スーパーボディと最強の美貌の悶える女 - JavBus</title>
                print('>>正在处理：', title)
                # 车牌号 識別碼:</span> <span style="color:#CC0000;">030619-872</span>
                nfo_dict['车牌'] = title_easy.split(' ', 1)[0]
                # 導演:</span> <a href="https://www.cdnbus.work/director/3hy">うさぴょん。</a></p>
                directorg = re.search(r'導演:</span> <a href=".+?">(.+?)</a>', jav_html)
                if str(directorg) != 'None':
                    nfo_dict['导演'] = directorg.group(1)
                else:
                    nfo_dict['导演'] = '未知导演'
                # 片商 製作商:</span> <a href="https://www.cdnbus.work/uncensored/studio/3n">カリビアンコム</a>
                studiog = re.search(r'製作商:</span> <a href=".+?">(.+?)</a>', bav_html)
                if str(studiog) != 'None':
                    nfo_dict['片商'] = studiog.group(1)
                else:
                    nfo_dict['片商'] = '未知片商'
                # 發行日期:</span> 2019-03-06</p>
                premieredg = re.search(r'發行日期:</span> (.+?)</p>', bav_html)
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
                runtimeg = re.search(r'長度:</span> (.+?)分鐘</p>', bav_html)
                if str(runtimeg) != 'None':
                    nfo_dict['片长'] = runtimeg.group(1)
                else:
                    nfo_dict['片长'] = '0'
                # 演员们 和 # 第一个演员
                actors = re.findall(r'<img src="https://images.javcdn.pw/actress/.+?" title="(.+?)"></a>', bav_html)
                if len(actors) != 0:
                    nfo_dict['首个女优'] = actors[0]
                    nfo_dict['全部女优'] = actors
                else:
                    nfo_dict['全部女优'] = ['未知演员']
                    nfo_dict['首个女优'] = '未知演员'
                nfo_dict['标题'] = nfo_dict['标题'].rstrip(nfo_dict['首个女优'])
                # 特点 <span class="genre"><a href="https://www.cdnbus.work/uncensored/genre/gre085">自慰</a></span>
                genres = re.findall(r'<span class="genre"><a href=".+?">(.+?)</a></span>', bav_html)
                genres = [i for i in genres if i != '字幕' and i != '高清' and i != '1080p' and i != '60fps']
                if len(genres) == 0:
                    genres = ['无特点']
                if '-c.' in file or '-C.' in file:
                    genres.append('中文字幕')
                # DVD封面cover
                cover_url = ''
                coverg = re.search(r'<a class="bigImage" href="(.+?)">', bav_html)  # 封面图片的正则对象
                if str(coverg) != 'None':
                    cover_url = coverg.group(1)
                #######################################################################
                # title = title.rstrip(nfo_dict['首个女优'])

                # 重命名视频
                new_mp4 = file.rstrip(video_type)
                if if_mp4 == '是':  # 新文件名
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
                    if cars_dic[car_num] > 1:    # 是CD1还是CDn？
                        cd_msg = '-cd' + str(srt.episodes)
                        new_mp4 += cd_msg
                    try:
                        # print(cars_dic)
                        # print(root + '\\' + file)
                        # print(root + '\\' + new_mp4 + video_type)
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
                        continue

                # 重命名文件夹
                new_root = root
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

                #写入nfo开始
                if if_nfo == '是':
                    # 开始写入nfo，这nfo格式是参考的emby的nfo
                    info_path = new_root + '\\' + new_mp4 + '.nfo'      #nfo存放的地址
                    f = open(info_path, 'w', encoding="utf-8")
                    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n"
                            "<movie>\n"
                            "  <plot></plot>\n"
                            "  <title>" + title + "</title>\n"
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
                    if simp_trad == '简':
                        for i in genres:
                            f.write("  <genre>" + gen_dict[i] + "</genre>\n")
                        for i in genres:
                            f.write("  <tag>" + gen_dict[i] + "</tag>\n")
                    else:
                        for i in genres:
                            f.write("  <genre>" + i + "</genre>\n")
                        for i in genres:
                            f.write("  <tag>" + i + "</tag>\n")
                    for i in nfo_dict['全部女优']:
                        f.write("  <actor>\n    <name>" + i + "</name>\n    <type>Actor</type>\n  </actor>\n")
                    f.write("</movie>\n")
                    f.close()
                    print('    >nfo收集完成')

                # 需要下载三张图片
                if if_jpg == '是':
                    # 默认的 全标题.jpg封面
                    if if_qunhui != '是':
                        fanart_path = new_root + '\\' + new_mp4 + '-fanart.jpg'
                        poster_path = new_root + '\\' + new_mp4 + '-poster.jpg'
                    else:
                        fanart_path = new_root + '\\' + new_mp4 + '.jpg'
                        poster_path = new_root + '\\' + new_mp4 + '.png'
                    # 下载 海报
                    try:
                        print('    >正在下载封面：', cover_url)
                        r = requests.get(cover_url, stream=True, timeout=10)
                        with open(fanart_path, 'wb') as f:
                            for chunk in r:
                                f.write(chunk)
                        print('    >fanart.jpg下载成功')
                    except:
                        try:
                            print('    >尝试下载fanart失败，正在尝试第二次下载...')
                            r = requests.get(cover_url, stream=True, timeout=10)
                            with open(fanart_path, 'wb') as f:
                                for chunk in r:
                                    f.write(chunk)
                            print('    >第二次下载成功')
                        except:
                            fail_times += 1
                            fail_message = '    >第' + str(fail_times) + '个失败！下载fanart.jpg失败：' + cover_url + '，\\' + new_root.lstrip(path) + '\\' + file + '\n'
                            print(fail_message, end='')
                            fail_list.append(fail_message)
                            write_fail(fail_message)
                            continue
                    # 下载 poster
                    # 默认的 全标题.jpg封面
                    # 裁剪 海报
                    img = Image.open(fanart_path)
                    w = img.width  # fanart的宽
                    h = img.height  # fanart的高
                    ew = int(0.653 * h)  # poster的宽
                    ex = w - ew  # x坐标
                    if if_face == '是':
                        ex = image_cut(fanart_path, client)  # 鼻子的x坐标  0.704 0.653
                        if ex + ew/2 > w:     # 鼻子 + 一半poster宽超出poster右边
                            ex = w - ew       # 以右边为poster
                        elif ex - ew/2 < 0:   # 鼻子 - 一半poster宽超出poster左边
                            ex = 0            # 以左边为poster
                        else:                 # 不会超出poster
                            ex = ex-ew/2       # 以鼻子为中心向两边扩展
                    try:
                        poster = img.crop((ex, 0, ex + ew, h))
                        poster.save(poster_path, quality=95)
                        print('    >poster.jpg裁剪成功')
                    except:
                        fail_times += 1
                        fail_message = '    >第' + str(fail_times) + '个失败！poster裁剪失败，请手动裁剪它吧：\\' + new_root.lstrip(
                            path) + '\\' + file + '\n'
                        print(fail_message, end='')
                        fail_list.append(fail_message)
                        write_fail(fail_message)
                        img.close()
                        continue
                    img.close()
                    if if_qunhui == '是':
                        shutil.copyfile(fanart_path, new_root + '\\Backdrop.jpg')

                # 收集女优头像
                if if_sculpture == '是':
                    for each_actor in nfo_dict['全部女优']:
                        exist_actor_path = '女优头像\\' + each_actor + '.jpg'
                        jpg_type = '.jpg'
                        if not os.path.exists(exist_actor_path):  # 女优图片还没有
                            exist_actor_path = '女优头像\\' + each_actor + '.png'
                            if not os.path.exists(exist_actor_path):  # 女优图片还没有
                                fail_times += 1
                                fail_message = '    >第' + str(
                                    fail_times) + '个失败！没有女优头像：' + each_actor + '，' + new_root + '\\' + file + '\n'
                                print(fail_message, end='')
                                fail_list.append(fail_message)
                                write_fail(fail_message)
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
                        actors_path = new_root + '\\.actors\\'
                        if not os.path.exists(actors_path):
                            os.makedirs(actors_path)
                        shutil.copyfile('女优头像\\' + each_actor + jpg_type,
                                        actors_path + each_actor + jpg_type)
                        print('    >女优头像收集完成：', each_actor)

            except:
                print('如果多次看到以下信息，请截图给作者！')
                print(traceback.format_exc())
                fail_times += 1
                fail_message = '    >第' + str(
                    fail_times) + '个失败！发生未知错误，如一直在该影片报错请联系作者：\\' + root.lstrip(path) + '\\' + file + '\n'
                print(fail_message, end='')
                fail_list.append(fail_message)
                write_fail(fail_message)
    # 完结撒花
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
