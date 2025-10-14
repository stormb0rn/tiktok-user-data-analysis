#!/usr/bin/env python3
"""
批量爬取 TikTok 用户并保存为 CSV - 并发版本
"""

import asyncio
import csv
import re
from datetime import datetime
from pathlib import Path
from scrape_user_tikhub import TikHubUserScraper


async def extract_username_from_url(url: str) -> str:
    """从 TikTok URL 中提取用户名"""
    url = url.strip()
    match = re.search(r'@([a-zA-Z0-9_\.]+)', url)
    if match:
        return match.group(1)
    return None


async def scrape_single_user(scraper, username: str, index: int, total: int) -> dict:
    """爬取单个用户"""
    print(f"[{index}/{total}] 正在爬取: @{username}")

    try:
        result = await scraper.fetch_user_profile(unique_id=username)

        if result and result.get('code') == 200:
            user_data = result.get('data', {}).get('user', {})

            row = {
                'username': username,
                'unique_id': user_data.get('unique_id', ''),
                'nickname': user_data.get('nickname', ''),
                'uid': user_data.get('uid', ''),
                'sec_uid': user_data.get('sec_uid', ''),
                'signature': user_data.get('signature', '').replace('\n', ' '),
                'follower_count': user_data.get('follower_count', 0),
                'following_count': user_data.get('following_count', 0),
                'total_favorited': user_data.get('total_favorited', 0),
                'aweme_count': user_data.get('aweme_count', 0),
                'visible_videos_count': user_data.get('visible_videos_count', 0),
                'verification_type': user_data.get('verification_type', 0),
                'verified': 'Yes' if user_data.get('verification_type', 0) > 0 else 'No',
                'bio_email': user_data.get('bio_email', ''),
                'category': user_data.get('category', ''),
                'account_type': user_data.get('account_type', 0),
                'avatar_larger_url': user_data.get('avatar_larger', {}).get('url_list', [''])[0],
                'profile_url': f"https://www.tiktok.com/@{username}",
                'scrape_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'scrape_status': 'success',
                'error_message': ''
            }

            print(f"  ✓ 成功 - 粉丝: {row['follower_count']:,}, 视频: {row['aweme_count']}")
            return row

        else:
            row = {
                'username': username,
                'scrape_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'scrape_status': 'failed',
                'error_message': result.get('message', 'Unknown error') if result else 'No response'
            }
            print(f"  ✗ 失败 - {row['error_message']}")
            return row

    except Exception as e:
        print(f"  ✗ 异常 - {str(e)}")
        row = {
            'username': username,
            'scrape_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'scrape_status': 'error',
            'error_message': str(e)
        }
        return row


async def scrape_users_to_csv_concurrent(
    user_list_file: str,
    output_csv: str,
    api_token: str,
    api_base_url: str = "https://api.tikhub.io",
    max_users: int = None,
    concurrency: int = 20
):
    """
    批量爬取用户并保存为 CSV - 使用并发

    Args:
        user_list_file: 用户列表文件路径
        output_csv: 输出 CSV 文件路径
        api_token: TikHub API Token
        api_base_url: API 基础 URL
        max_users: 最大爬取用户数（None 表示全部）
        concurrency: 并发数（同时进行的请求数）
    """
    print("="*60)
    print("批量爬取 TikTok 用户资料并保存为 CSV - 并发版本")
    print("="*60)
    print()

    # 读取用户列表
    print(f"读取用户列表: {user_list_file}")
    with open(user_list_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    # 提取用户名
    usernames = []
    for url in urls:
        username = await extract_username_from_url(url)
        if username:
            usernames.append(username)

    print(f"✓ 找到 {len(usernames)} 个用户")

    # 限制爬取数量
    if max_users:
        usernames = usernames[:max_users]
        print(f"✓ 限制爬取前 {max_users} 个用户")

    print(f"✓ 并发数: {concurrency} 个请求同时进行")
    print(f"✓ 预计速度: ~{concurrency} 请求/秒")
    print()

    # 创建爬虫实例
    scraper = TikHubUserScraper(
        api_token=api_token,
        base_url=api_base_url
    )

    # CSV 字段
    csv_fields = [
        'username',
        'unique_id',
        'nickname',
        'uid',
        'sec_uid',
        'signature',
        'follower_count',
        'following_count',
        'total_favorited',
        'aweme_count',
        'visible_videos_count',
        'verification_type',
        'verified',
        'bio_email',
        'category',
        'account_type',
        'avatar_larger_url',
        'profile_url',
        'scrape_time',
        'scrape_status',
        'error_message'
    ]

    # 创建 CSV 文件
    csv_file = Path(output_csv)
    csv_file.parent.mkdir(parents=True, exist_ok=True)

    results = []

    print("开始爬取...")
    print("-"*60)

    # 使用 Semaphore 限制并发数
    semaphore = asyncio.Semaphore(concurrency)

    async def scrape_with_semaphore(username, index, total):
        async with semaphore:
            return await scrape_single_user(scraper, username, index, total)

    # 创建所有任务
    tasks = [
        scrape_with_semaphore(username, i+1, len(usernames))
        for i, username in enumerate(usernames)
    ]

    # 并发执行所有任务
    results = await asyncio.gather(*tasks)

    print("-"*60)
    print()

    # 写入 CSV
    print(f"写入 CSV 文件: {csv_file}")
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)

    print(f"✓ CSV 文件已保存")
    print()

    # 统计
    success_count = sum(1 for r in results if r.get('scrape_status') == 'success')
    failed_count = len(results) - success_count

    print("="*60)
    print("爬取统计")
    print("="*60)
    print(f"总计: {len(results)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"成功率: {success_count/len(results)*100:.1f}%")
    print()
    print(f"✓ CSV 文件: {csv_file}")
    print("="*60)


async def main():
    """主函数"""
    # 配置
    USER_LIST_FILE = "/Users/jiajun/tiktok_user_scrape/Nova01 User list"
    OUTPUT_CSV = "/Users/jiajun/tiktok_user_scrape/output/nova01_users.csv"
    API_TOKEN = "YOUR_API_TOKEN_HERE"
    API_BASE_URL = "https://api.tikhub.io"
    MAX_USERS = None  # 爬取全部用户
    CONCURRENCY = 10  # 同时 10 个请求（平衡并发和限流）

    await scrape_users_to_csv_concurrent(
        user_list_file=USER_LIST_FILE,
        output_csv=OUTPUT_CSV,
        api_token=API_TOKEN,
        api_base_url=API_BASE_URL,
        max_users=MAX_USERS,
        concurrency=CONCURRENCY
    )


if __name__ == "__main__":
    asyncio.run(main())
