#!/usr/bin/env python3
"""
找出 Nova 02 中还没有爬取的用户
"""

import csv
import re
from pathlib import Path

# 读取用户列表
USER_LIST_FILE = "/Users/jiajun/tiktok_user_scrape/Nova 02 User List"
SCRAPED_CSV = "/Users/jiajun/tiktok_user_scrape/output/nova02_users.csv"
OUTPUT_FILE = "/Users/jiajun/tiktok_user_scrape/remaining_nova02_users.txt"

def extract_username(url):
    """从 URL 提取用户名"""
    url = url.strip()
    match = re.search(r'@([a-zA-Z0-9_\.]+)', url)
    if match:
        return match.group(1)
    return None

# 读取所有用户列表
print("读取用户列表...")
with open(USER_LIST_FILE, 'r', encoding='utf-8') as f:
    all_urls = [line.strip() for line in f if line.strip() and line.strip().startswith(('http://', 'https://'))]

all_usernames = []
for url in all_urls:
    username = extract_username(url)
    if username:
        all_usernames.append(username)

print(f"找到 {len(all_usernames)} 个用户")

# 读取已爬取的用户
scraped_usernames = set()
csv_path = Path(SCRAPED_CSV)
if csv_path.exists():
    print("读取已爬取的用户...")
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row.get('username', '')
            if username:
                scraped_usernames.add(username)
    print(f"已爬取 {len(scraped_usernames)} 个用户")
else:
    print("未找到已爬取的CSV文件")

# 找出未爬取的用户
remaining_usernames = [u for u in all_usernames if u not in scraped_usernames]

print(f"\n还需爬取 {len(remaining_usernames)} 个用户")

# 保存到文件
with open(OUTPUT_FILE, 'w') as f:
    f.write('\n'.join(remaining_usernames))

print(f"已保存到: {OUTPUT_FILE}")

# 统计
print("\n=== 统计 ===")
print(f"总用户数: {len(all_usernames)}")
print(f"已爬取: {len(scraped_usernames)}")
print(f"待爬取: {len(remaining_usernames)}")
print(f"进度: {len(scraped_usernames)/len(all_usernames)*100:.1f}%")
