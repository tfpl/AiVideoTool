import asyncio
import json
from datetime import datetime, timedelta
import os
import pandas as pd
from playwright.async_api import async_playwright
import random
import sys  # 用于退出脚本
COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__),"douyin_videos.xlsx")

def load_cookies_txt(file_path):
    """解析 cookies.txt 为 Playwright 可用格式"""
    print(f"加载cookies路径{file_path}")
    cookies = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) != 7:
                continue
            domain, flag, path, secure, expiry, name, value = parts
            expires = int(expiry) if expiry.isdigit() else 0  # 用 0 表示会话 cookie
            cookies.append({
                "domain": domain,
                "path": path,
                "secure": secure.upper() == "TRUE",
                "expires": expires,
                "name": name,
                "value": value,
                "httpOnly": False,
                "sameSite": "Lax"
            })
    return cookies

async def scrape_user_videos(user_url):
    async with async_playwright() as p:

        # 读取 Excel
        df = pd.read_excel(OUTPUT_FILE)

        # 检查列名
        for col in ["分享地址", "发布时间"]:
            if col not in df.columns:
                raise ValueError(f"Excel 中没有找到 '{col}' 列，请检查列名。")

        # 将“发布时间”列转换为 datetime 类型
        df["发布时间"] = pd.to_datetime(df["发布时间"], errors="coerce")

        # 获取今天的日期
        today = datetime.now().date()


        # print("\033[31mExcel 手动退出的，不需要请注释\033[0m")
        # sys.exit(0)
       

        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/121.0.0.0 Safari/537.36")
        )

        # 加载 cookies
        cookies = load_cookies_txt(COOKIES_FILE)
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()

        # 处理 JS 对话框（阻塞弹窗）
        async def on_dialog(dialog):
            try:
                await dialog.dismiss()
            except:
                pass
        page.on("dialog", lambda d: asyncio.create_task(on_dialog(d)))

        video_list = []

        # 异步处理接口响应
        async def process_response(response):
            url = response.url
            if "aweme/" in url and "/post" in url:
                try:
                    try:
                        data = await response.json()
                    except:
                        data = json.loads(await response.text())
                except:
                    return
                for item in data.get("aweme_list", []) or []:
                    v = item.get("video") or {}
                    
                    share_url = item.get("share_url") or {}
                    user_name = item.get("author") or {}
                    stats = item.get("statistics") or {}
                    play_addr = (v.get("play_addr") or {}).get("url_list") or []
                    cover_addr = (v.get("cover") or {}).get("url_list") or []
                    timestamp = item.get("create_time")
                    publish_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") if timestamp else None
                    title = item.get("desc")
                    if not title:  # 如果为空或None
                        title = publish_time  # 用发布时间替代
                    # 转换发布时间为 datetime
                    pub_time = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")

                    # 一周前的时间
                    one_week_ago = datetime.now() - timedelta(days=7)
                    if pub_time >= one_week_ago:
                        video_list.append({
                            "标题": title,
                            "作者": user_name.get("nickname"),
                            "评论": stats.get("comment_count"),
                            "点赞数": stats.get("digg_count"),
                            "视频地址(可能有水印)": play_addr[0] if play_addr else None,
                            "分享地址": share_url if share_url else None,
                            "封面": cover_addr[0] if cover_addr else None,
                            "发布时间": publish_time
                        })
                    if pub_time >= one_week_ago:
                        print(f"用户视频一周前发布，不下载：{title}")

        page.on("response", lambda r: asyncio.create_task(process_response(r)))

        print(f"正在打开用户主页：{user_url}")
        await page.goto(user_url, wait_until="domcontentloaded")

        # 尝试关闭可能的弹窗
        for txt in ["暂不", "以后再说", "取消", "关闭"]:
            try:
                await page.get_by_text(txt, exact=True).click(timeout=1500)
                break
            except:
                pass

        # 等待接口回调处理
        for _ in range(10):
            if video_list:
                break
            await asyncio.sleep(1)

        if not video_list:
            print("❌ 没有抓到任何视频，可能页面未加载或 cookies 失效。")

        # 读取已有 Excel 文件
        if os.path.exists(OUTPUT_FILE):
            existing_df = pd.read_excel(OUTPUT_FILE)
            # 清理 existing_df 列名空格
            existing_df.columns = existing_df.columns.str.strip()
            # 去掉 existing_df 空标题或空字段
            if "标题" in existing_df.columns:
                existing_df = existing_df[existing_df["标题"].notna() & (existing_df["标题"].str.strip() != "")]
            if "视频地址(可能有水印)" in existing_df.columns:
                existing_df = existing_df[existing_df["视频地址(可能有水印)"].notna() & (existing_df["视频地址(可能有水印)"].str.strip() != "")]
            if "封面" in existing_df.columns:
                existing_df = existing_df[existing_df["封面"].notna() & (existing_df["封面"].str.strip() != "")]
        else:
            existing_df = pd.DataFrame()

        # 新抓取的视频
        new_df = pd.DataFrame(video_list)
        # 清理列名空格
 

        if not existing_df.empty and not new_df.empty:
            # 找到新数据中与已有数据在三个字段任意一个重复的行
            mask = (
                new_df["标题"].notna() & new_df["标题"].isin(existing_df["标题"]) |
                new_df["视频地址(可能有水印)"].isin(existing_df["视频地址(可能有水印)"]) |
                new_df["封面"].isin(existing_df["封面"])  # 假设“分享链接”存在封面字段，也可以改成实际分享链接字段
            )
            # 只保留不重复的行
            new_df = new_df[~mask]

        # 合并新旧数据
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        # 保存回 Excel
        try:
            combined_df.to_excel(OUTPUT_FILE, index=False)
        except ModuleNotFoundError:
            csv_file = OUTPUT_FILE.replace(".xlsx", ".csv")
            combined_df.to_csv(csv_file, index=False, encoding="utf-8-sig")

        print(f"✅ 已保存 {len(combined_df)} 条视频到 {OUTPUT_FILE}")

        
        sleep_time = random.uniform(0, 2)  # 0~2 秒的随机浮点数
        print(f"⏳ 随机等待 {sleep_time:.2f} 秒再关闭浏览器...")
        await asyncio.sleep(sleep_time)
        await browser.close()
        
       

if __name__ == "__main__":
    user_url = "https://www.douyin.com/user/MS4wLjABAAAAz-Nssy-G6nNshJODTK3VpEpjWsH1pMHODDPexGS5K-D6EAo5iASK_qCGRb7M5Rbe?from_tab_name=main&vid=7533915948521999675"  # 替换为目标用户主页
    asyncio.run(scrape_user_videos(user_url))
    user_url2 = "https://www.douyin.com/user/MS4wLjABAAAAslofpLxb1ccBf6x1QC-hBZA8v4QpNg6GQjf8HQGQMiY?from_tab_name=main&vid=7538710619135053116"  # 替换为目标用户主页
    asyncio.run(scrape_user_videos(user_url2))
