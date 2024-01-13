# 该模块用于获取歌曲的封面、文件名、下载链接等信息
import re

import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}


class MusicInfo:
    def __init__(self, music_page: str):
        """
        :param music_page: str类型，歌曲页面链接
        """
        self._music_download_link = ''  # 歌曲下载链接
        self._cover_download_link = ''  # 封面下载链接
        self._lrc_text_split = ''  # 歌词下载链接
        self._music_name = ''  # 歌曲名

        self._goto_page(music_page)

    def _goto_page(self, music_page: str):
        """
        :param music_page: str类型，歌曲页面链接
        """
        response = requests.get(music_page, headers=headers)
        if response.status_code == 200:
            html = response.text
            self._get_music_name_and_lrc(html)
        else:
            print('响应状态码错误')

    def _get_music_name_and_lrc(self, html: str):
        """获取歌曲文件名"""
        if '该歌曲无权播放！歌曲相关资源已被删除！' not in html:
            pattern_music_downlink = '<a href="(https.+?mp3)"'
            re_result = re.findall(pattern_music_downlink, html)
            if re_result:
                self._music_download_link = re_result[0]

            pattern_cover_downlink = '</h1><img src="(http.+?jpg)"></div>'
            re_result = re.findall(pattern_cover_downlink, html)
            if re_result:
                self._cover_download_link = re_result[0]

            pattern_lrc_text = '</div><div class=gc><h3>LRC动态歌词下载</h3>(.+?)<br></div>'
            re_result = re.findall(pattern_lrc_text, html)
            if re_result:
                self._lrc_text_split = re_result[0].split('<br>')

            pattern_music_name = '<title>(.+?)《(.+?)》'
            re_result = re.findall(pattern_music_name, html)
            if re_result:
                self._music_name = f'{re_result[0][1]} - {re_result[0][0]}'

    def get_info(self):
        """返回信息"""
        info_dict = {
            'music_download_link': self._music_download_link,
            'cover_download_link': self._cover_download_link,
            'lrc_text_split': self._lrc_text_split,
            'music_name': self._music_name
        }

        return info_dict
