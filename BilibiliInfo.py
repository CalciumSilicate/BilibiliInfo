import re
import requests
import json
from mcdreforged.api.rtext import RAction, RText, RTextList

PLUGIN_METADATA = {
	'id': 'BilibiliInfo',
	'version': '1.0.0'
}

def simple_RText(message, text='', command='', action=RAction.run_command):
    Rtext = RText(message).set_hover_text(text).set_click_event(RAction.suggest_command, '')
    if command:
        Rtext.set_click_event(action, command)
    if text:
        Rtext.set_hover_text(text)
    else:
        Rtext.set_hover_text(command)
    return Rtext


def reformat_video(video: str):
    isBV = video.upper().startswith('BV')
    isAV = video.upper().startswith('AV')
    if isAV:
        video = video.lower()
    if isBV:
        video = 'BV' + video[2:]
    if isAV or isBV:
        return 'https://www.bilibili.com/video/{}'.format(video)
    elif video.upper().startswith('HTTP') and video.upper().find('://WWW.BILIBILI.COM/VIDEO') != -1:
        return video
    else:
        raise NameError


def pt_message(server, info, msg, tell=True, print_prefix=''):
    msg = print_prefix + msg
    if info.is_player and not tell:
        server.say(msg)
    else:
        server.reply(info, msg)


def print_message(server, info, msg, msg_prefix=''):
    if msg:
        for line in msg.splitlines():
            if info.is_player:
                server.say(f'{msg_prefix}{line}')
            else:
                server.reply(info, f'{msg_prefix}{line}')


def get_video_info(video: str = input, is_raw: bool = False, is_dumped: bool = False):
    try:
        html = requests.get(reformat_video(video)).text
    except NameError:
        return None
    title = re.findall('<h1 title="(.+?)" class', html)
    user_count = re.findall('},"stat":(.+?),"dynamic":"', html)[0]
    js_video = {
        'title': title[0],
        'vid_detail': json.loads(user_count),
        'url': reformat_video(video),
        'up': re.findall('name="author" content="(.+?)"><meta data-vue-meta', html)[0]
    }
    if is_raw:
        js_video['raw_html'] = html
    if is_dumped:
        js_video = json.dumps(js_video, indent=4)
    return js_video


def get_video_user(server, info, video: str):
    vid_info = get_video_info(video)
    if vid_info is None:
        return
    vid_detail: dict = vid_info['vid_detail']
    pt_message(server, info,
        RTextList(
            '标题:§e{}§r\n'.format(vid_info['title']),
            '点赞数 §e{}§r 弹幕数 §e{}§r \n评论数 §e{}§r 收藏数 §e{}§r \n硬币数 §e{}§r 分享数 §e{}§r \n播放数 §c{}§r up主 §c{}§r\n'. \
                format(
                vid_detail['like'],
                vid_detail['danmaku'],
                vid_detail['reply'],
                vid_detail['favorite'],
                vid_detail['coin'],
                vid_detail['share'],
                vid_detail['view'],
                vid_info['up']
            ),
            '网址:',
            simple_RText(
                '§b' + vid_info['url'] + ' (点击打开浏览器) §r',
                '点击链接打开网页',
                vid_info['url'],
                action=RAction.open_url
            ),
            simple_RText(
                ' §e[点击复制BV(AV)号]§r ',
                '点击复制BV号',
                video,
                action=RAction.copy_to_clipboard
            )
        )
    )


def on_info(server, info):
    if not info.content:
        return
    if not info.content.startswith('!!blbl'):
        get_video_user(server, info, info.content)
    else:
        get_video_user(server, info, info.content.split()[-1])
