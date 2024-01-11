# 主程序
import re

from lxml import html
from tqdm import tqdm

from down_music import *
from music_info import *

etree = html.etree
baseurl_search = r'https://www.gequbao.com/s/'
baseurl_homepage = r'https://www.gequbao.com'
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}


def get_search_result(keyword):
    """获取原始搜索结果文本"""
    url_search = baseurl_search + keyword
    response = requests.get(url_search, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print('响应状态码错误')


def get_urls(html_str: str):
    """利用正则提取网页链接"""
    pattern = r'<a href="(/music/\d+)" target'
    short_urls = re.findall(pattern, html_str)  # 短链接/music/402856
    urls = [baseurl_homepage + i for i in short_urls]  # 拼接完整链接
    return urls


def get_music_info(urls: list):
    """获取链接对应的链接字典"""
    url_info_dict = {}  # {url:{获取的info}...}
    for url in tqdm(urls, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        spider = MusicInfo(url)
        info_dict = spider.get_info()
        url_info_dict[url] = info_dict

    return url_info_dict


def show_music_list(url_info_dict: dict):
    """显示带编号的歌曲列表"""
    for index, info_dict in enumerate(url_info_dict.values(), start=1):
        music_name = info_dict['music_name']
        print(index, music_name)


def down_music(url, info_dict, retry_time=0):
    """
    下载歌曲
    :param retry_time: 重试次数，用于判断是否终止递归
    """
    if retry_time > 3:
        print('下载失败，已跳过')
        return
    spider = DownMusic(info_dict)
    music_name = spider.get_music_name()
    # 检查是否正确下载，如果错误则重新获取链接
    if spider.is_error():
        print(f'{music_name} 下载链接已失效，尝试重新获取')
        re_spider = MusicInfo(url)
        re_info_dict = re_spider.get_info()
        return down_music(url, re_info_dict, retry_time + 1)
    else:
        print(f'{music_name} 完成下载')


def main():
    while True:
        keyword = input('输入歌名/歌手，回车后查询：').strip()
        html_str = get_search_result(keyword)
        urls = get_urls(html_str)
        url_info_dict = get_music_info(urls)
        show_music_list(url_info_dict)

        while True:
            number = input('输入歌曲编号，回车后下载歌曲（输入0返回搜索栏，输入all下载全部）：').strip()
            if number == '0':
                break
            elif number == 'all':
                for select_url, select_info_dict in url_info_dict.items():
                    down_music(select_url, select_info_dict)
            else:
                select_url, select_info_dict = list(url_info_dict.items())[int(number) - 1]
                down_music(select_url, select_info_dict)


if __name__ == '__main__':
    main()
