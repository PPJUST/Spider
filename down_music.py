# 该模块用于获取歌曲的封面、文件名、下载链接等信息
import os

import requests
from mutagen.id3 import ID3, APIC, USLT


class DownMusic:
    """下载歌曲"""

    def __init__(self, info_dict: dict):
        self._music_download_link = info_dict['music_download_link']
        self._cover_download_link = info_dict['cover_download_link']
        self._lrc_download_link = info_dict['lrc_download_link']
        self._music_name = info_dict['music_name']

        if self._music_download_link:  # 如果没有获取到歌曲链接，则不进行下一步
            result = self._down_music()  # 歌曲链接有有效期，过期后无法下载文件
            if result:
                self._is_error = False
                self._down_lrc()
                self._down_cover()

                self._join_music_metadata()
                self._delete_useless_file()
            else:
                self._is_error = True
        else:
            self._is_error = True

    def is_error(self):
        """测试运行是否出错"""
        return self._is_error

    def _down_music(self):
        """下载歌曲"""
        filename = self._music_name + '.mp3'
        result = self._download_file(self._music_download_link, filename)
        return result

    def _down_lrc(self):
        """下载歌词"""
        filename = self._music_name + '.lrc'
        self._download_file(self._lrc_download_link, filename)

    def _down_cover(self):
        """下载封面"""
        filename = self._music_name + '.jpg'
        self._download_file(self._cover_download_link, filename)

    def _join_music_metadata(self):
        """拼合歌曲文件"""
        file_music = self._music_name + '.mp3'
        file_lrc = self._music_name + '.lrc'
        file_cover = self._music_name + '.jpg'

        audio = ID3(file_music)

        # 添加封面
        with open(file_cover, 'rb') as f:
            cover = f.read()
        audio['APIC'] = APIC(
            encoding=3,  # utf-8
            mime='image/jpeg',  # image/jpeg或image/png
            type=3,  # cover image
            desc=u'Cover',
            data=cover
        )

        # 添加歌词
        with open(file_lrc, 'r', encoding='utf-8') as f:
            lyrics = f.read()
        audio['USLT'] = USLT(
            encoding=3,  # utf-8
            lang='chi',  # 歌词语言
            desc=u'Lyrics',
            text=lyrics
        )

        audio.save()

    def _delete_useless_file(self):
        """合并后删除无用文件"""
        file_lrc = self._music_name + '.lrc'
        file_cover = self._music_name + '.jpg'

        os.remove(file_lrc)
        os.remove(file_cover)

    @staticmethod
    def _download_file(url, filename):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        with open(filename, 'wb') as f:
            f.write(response.content)

        if os.path.getsize(filename):
            return True
        else:
            return False
