#encoding: utf-8
#作者：龙磊
#日期：2019-5-10
#说明：此Python程序是用来下载今日头条中的单个视频
#使用方法：运行此程序，选择你要下载视频的分辨率，然后输入你想下载的今日头条的视频链接地址即可完成下载
import requests
from urllib.parse import urlencode
import re
import time
import random
from zlib import crc32
import base64

print('1、下载分辨率为360x640的普通视频。')
print('2、下载分辨率为480x854的清晰视频。')
print('3、下载分辨率为720x1280的高清视频。')
user_input = int(input('请输入你要下载的视频分辨率序号[1,2,3]：'))

UA_WEB_LIST = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3676.400 QQBrowser/10.4.3469.400",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
]
# 请求头信息
headers = {
    "User-Agent":random.choice(UA_WEB_LIST),
    "referer": 'http://www.365yg.com',
    "accept-language": "zh-CN,zh;q=0.9",
    'x-requested-with': 'XMLHttpRequest'
}

def video_id_title():
    video_watch_url = input('请输入你要下载的头条视频网址：')
    print('你输入的视频地址为：',video_watch_url)
    html = requests.get(video_watch_url,headers=headers).text

    #获取videoId和视频标题
    pattern = re.compile("videoId: '(.*?)'")
    video_id = pattern.findall(html)[0]
    # video_title = re.findall("abstract: '(.*?)'",html)[0]
    video_title = re.findall("<title>(.*?)</title>",html)[0]
    print(video_title)
    return (video_id,video_title)

def parse_base64_url(video_id):
    #生成16位随机数
    r = str(random.random())[2:]
    #填入从网页中获取的video_id和生成的r随机数组成url后面的路径
    path = '/video/urls/v/1/toutiao/mp4/{}?r={}'.format(video_id, r)
    #把path转换为bytes类型，然后使用crc32进行计算得出s的值
    s = bytes(path, encoding='utf-8')
    s = crc32(s)
    # 下面两个接口哪个都可以获取到通过base64加密的视频地址
    # 接口1：'http://i.snssdk.com/video/urls/v/1/toutiao/mp4/fbc23433928f4fcda094f155bd088af5?r=7806329635373263&s=379865165'
    # 接口2：http://ib.365yg.com/video/urls/v/1/toutiao/mp4/fbc23433928f4fcda094f155bd088af5?r=7806329635373263&s=379865165

    # 解析json数据完整地址拼接，第一个大括号填写变量path的内容，第二个大括号填写s的内容
    json_url = 'http://i.snssdk.com{}&s={}'.format(path, s)
    return json_url

#解析出视频真实的下载地址，视频宽高像素，视频大小等信息
def parse_video_download_url(json_url,video_title):
    #使用for循环遍历parse_base64_url函数返回的地址，下面定义的i是视频标题的下标
    video_data = []
    # 请求parse_base64_url函数返回的json_urls地址
    json_data = requests.get(json_url,headers)
    # 把请求的数据转换为json格式
    json_data = json_data.json()

    if user_input == 1:
        # 通过if判断是否存在以下三种分辨率的视频资源并获取相关视频信息
        if 'video_1' in json_data["data"]["video_list"]:
            #获取视频加密地址
            main_url1 = json_data['data']['video_list']['video_1']['main_url']
            # 获取清晰度
            definition1 = json_data['data']['video_list']['video_1']['definition']
            # 视频宽度单位像素
            vwidth1 = json_data['data']['video_list']['video_1']['vwidth']
            # 视频高度单位像素
            vheight1 = json_data['data']['video_list']['video_1']['vheight']
            # 视频宽高像素
            px1 = (str(vheight1) + 'x' + str(vwidth1))
            # 视频大小默认单位是字节,除以两个1024即把单位转化为MB，再用rount()方法保留两位小数
            video_size1 = str(round(json_data['data']['video_list']['video_1']['size']/1024/1024, 2)) + 'MB'
            # 把使用base64加密的视频地址转换为正确的视频下载地址
            video_url1 = str(base64.standard_b64decode(main_url1), encoding='utf-8')
            video1 = {1: video_url1, '视频宽高像素': px1, '视频大小': video_size1}
            video_data.append(video1)
        else:
            print(video_title,'没有360x640分辨率的视频资源！！！')

    elif user_input == 2:
        if 'video_2' in json_data["data"]["video_list"]:
            main_url2 = json_data['data']['video_list']['video_2']['main_url']
            definition2 = json_data['data']['video_list']['video_2']['definition']
            vwidth2 = json_data['data']['video_list']['video_2']['vwidth']
            vheight2 = json_data['data']['video_list']['video_2']['vheight']
            px2 = (str(vheight2) + 'x' + str(vwidth2))
            video_size2 = str(round(json_data['data']['video_list']['video_2']['size']/1024/1024, 2)) + 'MB'
            video_url2 = str(base64.standard_b64decode(main_url2), encoding='utf-8')
            video2 = {2: video_url2, '视频宽高像素': px2, '视频大小': video_size2}
            video_data.append(video2)
        else:
            print(video_title,'没有480x854分辨率的视频资源！！！')

    elif user_input == 3:
        if 'video_3' in json_data["data"]["video_list"]:
            main_url3 = json_data['data']['video_list']['video_3']['main_url']
            definition3 = json_data['data']['video_list']['video_3']['definition']
            vwidth3 = json_data['data']['video_list']['video_3']['vwidth']
            vheight3 = json_data['data']['video_list']['video_3']['vheight']
            px3 = (str(vheight3) + 'x' + str(vwidth3))
            video_size3 = str(round(json_data['data']['video_list']['video_3']['size']/1024/1024, 2)) + 'MB'
            video_url3 = str(base64.standard_b64decode(main_url3), encoding='utf-8')
            video3 = {3: video_url3, '视频宽高像素': px3, '视频大小': video_size3}
            video_data.append(video3)
        else:
            print(video_title, '没有720x1280分辨率的视频资源！！！')
    # print('用户选择的清晰度视频信息:',video_data)
    return video_data

#根据真正的视频地址进行下载指定清晰度的视频到本地保存
def download_video(video_data,video_title):
    for url in video_data:
        video_url = url[user_input]
        video_px = url['视频宽高像素']
        video_size = url['视频大小']
        print('视频真实下载地址为：',video_url)

        with requests.get(video_url, stream=True) as video:

            video_name = "{}_分辨率为{}_视频大小{}.mp4".format(video_title,video_px,video_size)
            print(video_name, '--------------正在下载中----------------------')
            with open(video_name, "wb") as f:
                # 保存视频字节流
                f.write(video.content)
                print(video_name, "下载成功")

if __name__ == '__main__':
    id_title = video_id_title()
    video_id = id_title[0]
    video_title = id_title[1]
    json_url = parse_base64_url(video_id)
    video_data = parse_video_download_url(json_url,video_title)
    download_video(video_data,video_title)
