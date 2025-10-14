#!/usr/bin/env python3
"""
重试所有失败的用户 - Nova 01 和 Nova 02
"""

import asyncio
import csv
from datetime import datetime
from pathlib import Path
from scrape_user_tikhub import TikHubUserScraper


async def scrape_single_user(scraper, username: str, index: int, total: int) -> dict:
    """爬取单个用户"""
    print(f"[{index}/{total}] 正在重试: @{username}")

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


async def retry_failed_users(
    failed_users_files: list,
    csv_outputs: list,
    api_token: str,
    api_base_url: str = "https://api.tikhub.io",
    concurrency: int = 10
):
    """重试所有失败的用户"""
    print("="*60)
    print("重试所有失败用户 - Nova 01 & Nova 02")
    print("="*60)
    print()

    # 读取所有失败用户
    all_failed_usernames = []
    for failed_file in failed_users_files:
        if Path(failed_file).exists():
            with open(failed_file, 'r', encoding='utf-8') as f:
                usernames = [line.strip() for line in f if line.strip()]
                all_failed_usernames.extend(usernames)
                print(f"✓ {failed_file}: {len(usernames)} 个失败用户")

    print(f"\n✓ 总计需要重试: {len(all_failed_usernames)} 个用户")
    print(f"✓ 并发数: {concurrency} 个请求同时进行")
    print(f"✓ 预计完成时间: ~{len(all_failed_usernames)/concurrency:.1f} 秒 ({len(all_failed_usernames)/concurrency/60:.1f} 分钟)")
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

    print("开始重试...")
    print("-"*60)

    # 使用 Semaphore 限制并发数
    semaphore = asyncio.Semaphore(concurrency)

    async def scrape_with_semaphore(username, index, total):
        async with semaphore:
            return await scrape_single_user(scraper, username, index, total)

    # 创建所有任务
    tasks = [
        scrape_with_semaphore(username, i+1, len(all_failed_usernames))
        for i, username in enumerate(all_failed_usernames)
    ]

    # 并发执行所有任务
    results = await asyncio.gather(*tasks)

    print("-"*60)
    print()

    # 按用户名分组结果，用于更新对应的 CSV
    results_by_username = {r['username']: r for r in results}

    # 更新每个 CSV 文件
    for csv_file in csv_outputs:
        csv_path = Path(csv_file)
        if not csv_path.exists():
            print(f"⚠ CSV 文件不存在: {csv_file}")
            continue

        print(f"更新 CSV 文件: {csv_file}")

        # 读取现有数据
        existing_data = {}
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_data[row['username']] = row

        # 更新成功的记录
        updated_count = 0
        for username, result in results_by_username.items():
            if username in existing_data and result.get('scrape_status') == 'success':
                existing_data[username] = result
                updated_count += 1

        # 写回 CSV
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(existing_data.values())

        print(f"  ✓ 更新了 {updated_count} 条记录")

        # 统计该 CSV 的成功率
        total_success = sum(1 for r in existing_data.values() if r.get('scrape_status') == 'success')
        print(f"  ✓ 总成功率: {total_success}/{len(existing_data)} ({total_success/len(existing_data)*100:.1f}%)")
        print()

    # 总体统计
    success_count = sum(1 for r in results if r.get('scrape_status') == 'success')
    failed_count = len(results) - success_count

    print("="*60)
    print("重试统计")
    print("="*60)
    print(f"重试总数: {len(results)}")
    print(f"本次成功: {success_count}")
    print(f"仍然失败: {failed_count}")
    print(f"成功率: {success_count/len(results)*100:.1f}%")
    print()

    # 保存仍然失败的用户
    still_failed = [r['username'] for r in results if r.get('scrape_status') != 'success']
    if still_failed:
        with open('still_failed_users_final.txt', 'w') as f:
            f.write('\n'.join(still_failed))
        print(f"仍然失败的用户已保存到: still_failed_users_final.txt ({len(still_failed)}个)")
    else:
        print("🎉 所有用户都成功爬取！")

    print("="*60)


async def main():
    """主函数"""
    FAILED_USERS_FILES = [
        "/Users/jiajun/tiktok_user_scrape/still_failed_users.txt",  # Nova 01
        "/Users/jiajun/tiktok_user_scrape/failed_users_nova02_final.txt"  # Nova 02
    ]

    CSV_OUTPUTS = [
        "/Users/jiajun/tiktok_user_scrape/output/nova01_users.csv",
        "/Users/jiajun/tiktok_user_scrape/output/nova02_users.csv"
    ]

    API_TOKEN = "YOUR_API_TOKEN_HERE"
    API_BASE_URL = "https://api.tikhub.io"
    CONCURRENCY = 10  # 同时 10 个请求

    await retry_failed_users(
        failed_users_files=FAILED_USERS_FILES,
        csv_outputs=CSV_OUTPUTS,
        api_token=API_TOKEN,
        api_base_url=API_BASE_URL,
        concurrency=CONCURRENCY
    )


if __name__ == "__main__":
    asyncio.run(main())
