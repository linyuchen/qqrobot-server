import base64
import time
import queue
import threading
import traceback
from enum import Enum
from io import BytesIO
from typing import TypedDict

import win32api
import win32clipboard
import win32con
import win32gui
from PIL import Image
from pywinauto import keyboard
from flask import Flask, request

TEXT_MAX_LEN = 3000


class MsgType(Enum):
    TEXT = "Plain"
    IMAGE = "Image"
    AT = "At"


class MessageData(TypedDict):
    type: MsgType
    data: str


class Message(TypedDict):
    qq_group_name: str
    data: list[MessageData]


def paste(data, is_image, win=None):
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
    except:
        paste(data, is_image, win)
        return
    try:
        if is_image:
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        else:
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, data)
    except:
        paste(data, is_image, win)
        return
    # keyboard.send_keys("^v")  # 这个在Hyper-V虚拟机中不好使
    win32api.PostMessage(win, win32con.WM_PASTE, 0, 0)
    # win32api.keybd_event(17, 0, 0, 0)                           # ctrl的键位码是17
    # time.sleep(0.1)
    # win32api.keybd_event(86, 0, 0, 0)                           # v的键位码是86
    # time.sleep(0.1)
    # win32api.keybd_event(86, 0, win32con.KEYEVENTF_KEYUP, 0)    # 释放按键
    # win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
    if not is_image:
        if len(data) >= TEXT_MAX_LEN:  # 如果是长文本，先发送，不然文字太多不允许发送
            time.sleep(0.5)
            keyboard.send_keys("{ENTER}")
    try:
        win32clipboard.CloseClipboard()
    except:
        pass


def split_long_msg(msg: Message) -> Message:
    new_msg = Message(qq_group_name=msg["qq_group_name"], data=[])
    for msg_data in msg["data"]:
        if msg_data.get("type") in [MsgType.TEXT.value, MsgType.TEXT]:
            text = msg_data["data"]
            if len(text) >= TEXT_MAX_LEN:
                for i in range(0, len(text), TEXT_MAX_LEN):
                    new_msg["data"].append({
                        "type": MsgType.TEXT, "data": text[i:i + TEXT_MAX_LEN]
                    })
            else:
                new_msg["data"].append(msg_data)
        else:
            new_msg["data"].append(msg_data)
    return new_msg


def send_msg(msg: Message):
    interval = 1
    window_handle = win32gui.FindWindow(None, msg["qq_group_name"])
    try_count = 0
    while True:
        if try_count >= 5:
            raise Exception("找不到窗口")
        try:
            try_count += 1
            win32gui.SetForegroundWindow(window_handle)
            break
        except:
            traceback.print_exc()
            time.sleep(interval)
    time.sleep(interval)
    msg = split_long_msg(msg)
    for msg_data in msg["data"]:
        match msg_data.get("type"):
            case MsgType.TEXT.value | MsgType.TEXT:
                text = msg_data["data"]
                paste(text, False, window_handle)
            case MsgType.IMAGE | MsgType.IMAGE.value:
                image_data = base64.decodebytes(msg_data["data"].encode("utf-8"))
                fp = BytesIO(image_data)
                im = Image.open(fp)
                output = BytesIO()
                im.save(output, format="BMP")
                data = output.getvalue()[14:]
                paste(data, True, window_handle)
                time.sleep(1)
            case MsgType.AT | MsgType.AT.value:
                text = msg_data["data"]
                paste(text, False, window_handle)
                time.sleep(0.5)
                keyboard.send_keys("{ENTER}")
                time.sleep(0.5)
                keyboard.send_keys("+{ENTER}")
        time.sleep(interval)

    keyboard.send_keys("{ENTER}")


app = Flask(__name__)

# 创建一个队列对象
message_queue = queue.Queue()


@app.route('/', methods=['POST'])
def handle_post():
    # 解析 POST 请求中的 JSON 数据
    data = request.get_json()
    # 将 JSON 数据转换为 Message 类型
    # if data.get("key") == "linyuchen":
    message = Message(**data)
    # 将消息放入队列中
    message_queue.put(message)
    # 返回响应
    return 'OK'


def handle_queue():
    while True:
        message = message_queue.get()
        try:
            send_msg(message)
        except:
            traceback.print_exc()
        time.sleep(0.1)


def main():
    # 创建一个新线程，用于处理消息队列
    queue_thread = threading.Thread(target=handle_queue)
    # queue_thread.daemon = True
    queue_thread.start()
    app.run(host='0.0.0.0', port=8088)


if __name__ == '__main__':
    main()
