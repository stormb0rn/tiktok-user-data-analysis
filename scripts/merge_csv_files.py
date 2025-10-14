#!/usr/bin/env python3
"""
合并 Nova 01 和 Nova 02 的 CSV 文件
"""

import csv
from pathlib import Path

def merge_csv_files(
    input_files: list,
    output_file: str
):
    """合并多个 CSV 文件"""
    print("="*60)
    print("合并 CSV 文件")
    print("="*60)
    print()

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

    # 使用字典去重（以 username 为 key）
    all_data = {}

    # 读取所有 CSV 文件
    for csv_file in input_files:
        csv_path = Path(csv_file)
        if not csv_path.exists():
            print(f"⚠ 文件不存在: {csv_file}")
            continue

        print(f"读取: {csv_file}")
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                username = row.get('username', '')
                if username:
                    # 如果用户已存在，保留成功的记录或更新的记录
                    if username in all_data:
                        # 如果新记录是成功的，或者旧记录是失败的，则更新
                        old_status = all_data[username].get('scrape_status')
                        new_status = row.get('scrape_status')
                        if new_status == 'success' or old_status != 'success':
                            all_data[username] = row
                    else:
                        all_data[username] = row
                    count += 1
        print(f"  ✓ 读取 {count} 条记录")

    print()
    print(f"合并后总计: {len(all_data)} 个唯一用户")

    # 统计成功和失败
    success_count = sum(1 for r in all_data.values() if r.get('scrape_status') == 'success')
    failed_count = len(all_data) - success_count

    print(f"  成功: {success_count} ({success_count/len(all_data)*100:.1f}%)")
    print(f"  失败: {failed_count} ({failed_count/len(all_data)*100:.1f}%)")
    print()

    # 写入合并后的 CSV
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"写入合并后的文件: {output_file}")
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction='ignore')
        writer.writeheader()
        # 按 username 排序
        sorted_data = sorted(all_data.values(), key=lambda x: x.get('username', '').lower())
        writer.writerows(sorted_data)

    print(f"✓ 合并完成！")
    print()

    print("="*60)
    print("合并统计")
    print("="*60)
    print(f"输入文件数: {len(input_files)}")
    print(f"合并后总用户数: {len(all_data)}")
    print(f"成功用户数: {success_count}")
    print(f"失败用户数: {failed_count}")
    print(f"输出文件: {output_file}")
    print(f"文件大小: {output_path.stat().st_size / 1024:.1f} KB")
    print("="*60)


if __name__ == "__main__":
    INPUT_FILES = [
        "/Users/jiajun/tiktok_user_scrape/output/nova01_users.csv",
        "/Users/jiajun/tiktok_user_scrape/output/nova02_users.csv"
    ]

    OUTPUT_FILE = "/Users/jiajun/tiktok_user_scrape/output/merged_all_users.csv"

    merge_csv_files(INPUT_FILES, OUTPUT_FILE)
