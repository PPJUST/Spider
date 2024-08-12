import multiprocessing
import os
import re
import shutil

import natsort

import requests
from bs4 import BeautifulSoup

temp_folder = 'temp'
base_url = 'https://www.bqgoo.cc'
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}
pattern_chapter_info = r'<dd><a href ="(.+?html)">([^<]+)<.+?dd>'
pattern_book_title = r'<meta property="og:novel:book_name" content="(.+?)"'


def get_chapter_url_and_title(book_url: str):
    """爬取章节url和标题
    :return: str：文章标题；list，顺序index，内部元素为元祖(章节路径, 章节标题)"""
    print('爬取章节url和标题')
    response = requests.get(book_url, headers=headers)
    if response.status_code == 200:
        html = response.text
        html_split = html.splitlines()
        # 提取书名
        book_title = '未知'
        for line in html_split:
            match_ = re.match(pattern_book_title, line.strip())
            if match_:
                book_title = match_.group(1)
                break

        # 提取章节信息
        chapter_info_list = []  # 顺序index，内部元素为元祖(章节路径, 章节标题)
        for line in html_split:
            line = line.strip()
            match_ = re.match(pattern_chapter_info, line)
            if match_:
                url_half = match_.group(1)
                url_total = base_url + url_half
                title = match_.group(2)
                group_ = (url_total, title)
                chapter_info_list.append(group_)

        return book_title, chapter_info_list


def download_chapter_text(chapter_index, chapter_url, chapter_title):
    """爬取章节内容，并保存到本地临时目录"""
    print(f'爬取章节内容，当前章节编号：{chapter_index}，章节名：{chapter_title}')
    response = requests.get(chapter_url, headers=headers)
    if response.status_code == 200:
        # 提取内容
        soup = BeautifulSoup(response.text, 'html.parser')
        div = soup.find('div', id='chaptercontent')
        chapter_text = div.get_text()
        chapter_text_split = chapter_text.split('　　')
        # 写入本地文件
        print(f'保存第{chapter_index}章正文')
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)
        txt_path = os.path.join(temp_folder, f'{chapter_index}_{chapter_title}.txt')
        with open(txt_path, 'w', encoding='utf-8') as tw:
            # 头部空1行
            tw.write('\n' * 1)
            # 写入标题
            tw.write(chapter_title + '\n')
            # 写入正文
            for line in chapter_text_split:
                if chapter_title in line or re.match(r'第.+?章', line):  # 剔除正文中可能包含的标题
                    continue
                if not line.strip():  # 剔除空文本
                    continue
                # 剔除广告
                if '收藏本站' in line or '点此报错' in line:
                    continue
                line_text = '  ' + line + '\n' * 2  # 段落前空两格+段间距两行
                tw.write(line_text)
            # 尾部空1行
            tw.write('\n' * 1)


def multiprocessing_download_chapter_text(chapter_info_list):
    """多进程下载"""
    pool = multiprocessing.Pool()
    for index, info in enumerate(chapter_info_list, start=1):
        chapter_url, chapter_title = info
        pool.apply_async(download_chapter_text, args=(index, chapter_url, chapter_title))
    pool.close()
    pool.join()


def join_texts(book_title):
    """合并下载的正文文本文件"""
    print('合并所有章节的文本')
    # 提取所有文本文件路径
    _files = os.listdir(temp_folder)
    files = [os.path.join(temp_folder, i) for i in _files]
    files = natsort.natsorted(files)  # 必须排序，否则章节是乱序的
    # 逐个读取内容
    txt_joined = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as tr:
            text = tr.read()
            txt_joined.append(text)
    # 保存完整文本
    with open(f'{book_title}.txt', 'w', encoding='utf-8') as tw:
        tw.writelines(txt_joined)
    # 删除临时文本文件及临时文件夹
    shutil.rmtree(temp_folder)
    print('完成全部任务')
    print('*' * 50)


def main(book_url):
    # 获取章节链接和标题
    book_title, chapter_info_list = get_chapter_url_and_title(book_url)
    # 逐章爬取正文
    multiprocessing_download_chapter_text(chapter_info_list)
    # 合并所有下载的章节
    join_texts(book_title)


if __name__ == '__main__':
    print('小说爬虫，仅支持www.bqgoo.cc')
    print('*' * 50)
    while True:
        _book_url = input('输入小说完整链接（示例：https://www.bqgoo.cc/shu/11424/）：')
        main(_book_url)
