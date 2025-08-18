# -*- coding: utf-8 -*-
"""
Python GUI 自动输入工具
功能:
1. 启动 GUI 程序
2. 等待程序完全打开
3. 模拟键盘输入参数（5 → 2 → 2 → 文件路径）
"""

import pyautogui  # 需要 pip install pyautogui
import pyperclip  # 需要 pip install pyperclip
import subprocess
import time
import os

# ---------------- 执行爬虫脚本 ----------------
print("开始执行 douyin_scraper.py 爬取视频...")
subprocess.run(["python", ".\DouYinScraper\douyin_scraper.py"], check=True)
print("爬虫执行完成")

# ---------------- 执行处理分享链接 ----------------
print("开始执行 ExcelUtils.py 执行处理分享链接...")
subprocess.run(["python", ".\DouYinScraper\ExcelUtils.py"], check=True)
print("分享链接获取完成")


# ---------------- 设置参数 ----------------
exe_path = r".\TikTokDownloader_V5.6_Windows_X64\main.exe"  # GUI 程序路径
file_path = r"D:\tools\AI信息收集转化整理工具链\DouYinScraper\share_links.txt"

# ---------------- 启动 GUI 程序 ----------------
if not os.path.exists(exe_path):
    raise FileNotFoundError(f"找不到 exe 文件: {exe_path}")
# ---------------- 启动程序 ----------------
process = subprocess.Popen(
    exe_path,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    shell=True
)

print("启动程序，开始监控输出...")

# ---------------- 监控程序输出 ----------------
success = False
download_started = False

while True:
    line = process.stdout.readline()
    if not line:
        if process.poll() is not None:  # 程序结束
            break
        print("[程序输出] 开始睡8分钟")
        time.sleep(500)
        continue
    line = line.strip()
    print(f"[程序输出] {line}")

    # ---------------- 根据提示输入 ----------------
    if not download_started:
        if "Switch to English" in line:
            time.sleep(0.25)
            pyautogui.typewrite("5")
            pyautogui.press("enter")
            time.sleep(0.25)

        elif "批量下载视频原画(TikTok)" in line:
            time.sleep(0.25)
            pyautogui.typewrite("2")
            pyautogui.press("enter")
            time.sleep(0.25)

        elif "从文本文档读取待采集的作品链接" in line:
            time.sleep(0.25)
            pyautogui.typewrite("2")
            pyautogui.press("enter")
            time.sleep(0.25)
            break

   
# 粘贴中文路径
pyperclip.copy(file_path)
pyautogui.hotkey("ctrl", "v")
pyautogui.press("enter")
download_started = True
print(f"\033[32m请耐心等待几分钟，下载中\033[0m")

while True:
    line = process.stdout.readline()
    if not line:
        if process.poll() is not None:  # 程序结束
            break
        print("[程序输出] 开始睡8分钟")
        time.sleep(500)
        continue
    line = line.strip()
    # ---------------- 判断下载完成 ----------------
    if  "已退出批量下载链接作品" in line:
        time.sleep(5)
        success = True
            # 结束外部程序
        process.terminate()  # 温和结束
        # process.kill()    # 强制结束，也可以使用
        break
    if "请输入文本文档路径" not in line:
        print(f"[程序输出] {line}")
   

# ---------------- 判断结果 ----------------
if success:
    print("\033[32m 采集视频成功 ✅\033[0m")
else:
    print("\033[31m错误信息：程序失败\033[0m")  # 红色

bat_file = r"D:\tools\AI信息收集转化整理工具链\博主视频分析处理\whisper_and_convert.bat"

# 启动 BAT 文件
process = subprocess.Popen(
    bat_file,
    stdout=subprocess.PIPE,      # 捕获标准输出
    stderr=subprocess.STDOUT,    # 合并标准错误
    encoding='utf-8',        # 指定 UTF-8 编码
    errors='replace',        # 遇到非法字符用 � 替代
    text=True,                   # 输出为字符串
    shell=True                   # Windows 下需要 shell=True
)

# 实时读取输出
while True:
    line = process.stdout.readline()
    if not line:
        if process.poll() is not None:
            break
        continue
    try:
        print(line.strip())
    except UnicodeDecodeError:
        # 遇到无法解码字符时替换
        print(line.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))


# 获取退出码
if process.returncode == 0:
    print("BAT 脚本执行成功 ✅")
else:
    print(f"BAT 脚本执行失败 ❌，退出码 {process.returncode}")
process.terminate()  # 温和结束
