import requests
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import threading
from datetime import datetime

def fetch_danmaku(video_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # 获取视频的 CID
    response = requests.get(video_url, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'  # 设置编码
    cid = response.text.split('"cid":')[1].split(',')[0]

    # 获取弹幕 XML
    danmaku_url = f'https://comment.bilibili.com/{cid}.xml'
    response = requests.get(danmaku_url, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'  # 设置编码
    danmaku_xml = response.text

    # 解析弹幕 XML
    root = ET.fromstring(danmaku_xml)
    danmaku_list = []
    for idx, d in enumerate(root.findall('.//d'), start=1):
        p = d.attrib['p'].split(',')
        timestamp = int(p[4])
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')  # 转换为标准日期格式
        sender = p[6]  # 发送者 ID
        content = d.text  # 弹幕内容
        danmaku_list.append(f"序号: {idx}, 日期: {date}, 发送者: {sender}, 内容: {content}")

    return danmaku_list

def start_fetching():
    def task():
        progress_bar.start()  # 开始进度条
        root.update_idletasks()  # 更新界面

        video_url = url_entry.get()
        danmaku_list = fetch_danmaku(video_url)

        text_area.delete(1.0, tk.END)
        for danmaku in danmaku_list:
            text_area.insert(tk.INSERT, danmaku + "\n")

        progress_bar.stop()  # 停止进度条

    threading.Thread(target=task).start()

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

def copy_text():
    text_area.event_generate("<<Copy>>")

def cut_text():
    text_area.event_generate("<<Cut>>")

def paste_text():
    text_area.event_generate("<<Paste>>")

def select_all():
    text_area.tag_add(tk.SEL, "1.0", tk.END)
    text_area.mark_set(tk.INSERT, "1.0")
    text_area.see(tk.INSERT)

# 创建主窗口
root = tk.Tk()
root.title("Bilibili 弹幕提取器")

# 创建一个输入框来输入视频 URL
url_label = tk.Label(root, text="视频 URL:")
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)
url_entry.insert(0, 'https://www.bilibili.com/video/BV168PKeHETd')  # 默认示例视频 URL

# 创建一个滚动文本框来显示弹幕内容
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
text_area.pack(padx=10, pady=10)

# 创建右键菜单
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="复制", command=copy_text)
context_menu.add_command(label="剪切", command=cut_text)
context_menu.add_command(label="粘贴", command=paste_text)
context_menu.add_command(label="全选", command=select_all)

# 绑定右键菜单
text_area.bind("<Button-3>", show_context_menu)

# 创建一个按钮来触发弹幕提取
fetch_button = tk.Button(root, text="获取弹幕内容", command=start_fetching)
fetch_button.pack(pady=10)

# 创建一个进度条
progress_bar = ttk.Progressbar(root, mode='indeterminate')
progress_bar.pack(pady=10)

# 运行主循环
root.mainloop()