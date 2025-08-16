import pandas as pd
from datetime import datetime, timedelta
import os

# 文件路径
excel_file = os.path.join(os.path.dirname(__file__),"douyin_videos.xlsx")
txt_file = os.path.join(os.path.dirname(__file__),"share_links.txt")

# 读取 Excel
df = pd.read_excel(excel_file)

# 检查列名
for col in ["分享地址", "发布时间"]:
    if col not in df.columns:
        raise ValueError(f"Excel 中没有找到 '{col}' 列，请检查列名。")

# 将“发布时间”列转换为 datetime 类型
df["发布时间"] = pd.to_datetime(df["发布时间"], errors="coerce")

# 获取今天和昨天的日期
today = datetime.now().date()
yesterday = today - timedelta(days=1)

# 过滤只保留昨天、今天或未来的记录
filtered_df = df[df["发布时间"].dt.date >= yesterday]

# 提取分享地址
new_links = filtered_df["分享地址"].dropna().astype(str).tolist()

# 如果 TXT 已存在，读取已有链接
existing_links = set()
if os.path.exists(txt_file):
    with open(txt_file, "r", encoding="utf-8") as f:
        existing_links = set(line.strip() for line in f if line.strip())

# 去掉重复链接
unique_links = [link for link in new_links if link not in existing_links]

# 写入 TXT（追加模式）
with open(txt_file, "a", encoding="utf-8") as f:
    for link in unique_links:
        f.write(link + "\n")

print(f"✅ 已追加 {len(unique_links)} 条分享地址到 {txt_file}")
