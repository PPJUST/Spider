# 该模块用于获取歌曲的封面、文件名、下载链接等信息

from playwright.sync_api import sync_playwright


class MusicInfo:
    def __init__(self, music_page: str):
        """
        :param music_page: str类型，歌曲页面链接
        """
        self._music_download_link = ''  # 歌曲下载链接
        self._cover_download_link = ''  # 封面下载链接
        self._lrc_download_link = ''  # 歌词下载链接
        self._music_name = ''  # 歌曲名

        self._goto_page(music_page)

    def _goto_page(self, music_page: str):
        """
        :param music_page: str类型，歌曲页面链接
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on('response', self._on_response)  # 响应请求
            page.goto(music_page)
            page.wait_for_load_state('networkidle')
            html = page.content()  # 获取页面源码
            browser.close()

        self._get_music_name_and_lrc(html)

    def _on_response(self, response):
        state = response.status  # 状态码
        url = response.url  # 链接
        # print(f'Statue {state}: {url}')
        # 酷我接口
        if 'kuwo' in url and '.mp3' in url:  # 提取歌曲下载链接
            self._music_download_link = url
        elif 'kuwo' in url and '.jpg' in url:  # 提取封面
            self._cover_download_link = url
        # 网易云接口
        elif 'music.126' in url and '.mp3' in url:  # 提取歌曲下载链接
            self._music_download_link = url
        elif 'music.126' in url and'.jpg' in url:  # 提取封面
            self._cover_download_link = url


    def _get_music_name_and_lrc(self, html: str):
        """获取歌曲文件名"""
        html_lines = html.split('\n')
        for line in html_lines:
            # print(f'Line: {line}')
            if 'description' in line:  # 提取歌曲名称
                # <meta name="description" content="青花瓷-周杰伦.mp3免费在线下载播放,歌曲宝在线音乐搜索
                split1 = line.find('content=')
                split2 = line.find('.mp3')
                music_name = line[split1 + len('content=') + 1:split2]
                self._music_name = music_name

            elif 'btn-download-lrc' in line and 'href' in line:  # 提取歌词
                # <a id="btn-download-lrc" href="/download/lrc/1655094" class="btn btn-primary"
                split1 = line.find('href=')
                split2 = line.find(' class')
                short_lrc_url = line[split1 + len('href=') + 1:split2 - 1]
                lrc_download_link = 'https://www.gequbao.com' + short_lrc_url
                self._lrc_download_link = lrc_download_link

    def get_info(self):
        """返回信息"""
        info_dict = {
            'music_download_link': self._music_download_link,
            'cover_download_link': self._cover_download_link,
            'lrc_download_link': self._lrc_download_link,
            'music_name': self._music_name
        }

        return info_dict

