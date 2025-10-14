#!/usr/bin/env python3
"""
实时进度条监控爬取进度
"""

import time
import re
import sys
from pathlib import Path


def get_progress_from_log(log_file):
    """从日志文件中提取当前进度"""
    try:
        # 读取最后 100 行
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 从后往前查找进度信息
        for line in reversed(lines[-100:]):
            # 匹配 [123/5339] 格式
            match = re.search(r'\[(\d+)/(\d+)\]', line)
            if match:
                current = int(match.group(1))
                total = int(match.group(2))
                return current, total

        return 0, 5339
    except:
        return 0, 5339


def draw_progress_bar(current, total, bar_length=50, start_time=None):
    """绘制进度条"""
    progress = current / total
    filled = int(bar_length * progress)
    bar = '█' * filled + '░' * (bar_length - filled)

    percentage = progress * 100

    # 计算速度和预计完成时间
    if start_time and current > 0:
        elapsed = time.time() - start_time
        speed = current / elapsed
        remaining = total - current
        eta_seconds = remaining / speed if speed > 0 else 0
        eta_minutes = eta_seconds / 60

        # 格式化输出
        sys.stdout.write(f'\r[{bar}] {current}/{total} ({percentage:.1f}%) | '
                        f'速度: {speed:.1f}/s | 剩余: {eta_minutes:.1f}分钟')
    else:
        sys.stdout.write(f'\r[{bar}] {current}/{total} ({percentage:.1f}%)')

    sys.stdout.flush()


def monitor_progress(log_file, refresh_interval=2):
    """监控进度"""
    log_path = Path(log_file)

    if not log_path.exists():
        print(f"❌ 日志文件不存在: {log_file}")
        return

    print("="*70)
    print("📊 TikTok 用户爬取进度监控")
    print("="*70)
    print(f"📝 日志文件: {log_file}")
    print(f"🔄 刷新间隔: {refresh_interval} 秒")
    print()
    print("按 Ctrl+C 停止监控")
    print("-"*70)
    print()

    start_time = time.time()
    last_current = 0

    try:
        while True:
            current, total = get_progress_from_log(log_file)

            # 绘制进度条
            draw_progress_bar(current, total, bar_length=50, start_time=start_time)

            # 检查是否完成
            if current >= total and current > 0:
                print()
                print()
                print("="*70)
                print("✅ 爬取完成！")
                print("="*70)

                elapsed = time.time() - start_time
                avg_speed = current / elapsed

                print(f"总用户数: {current:,}")
                print(f"总耗时: {elapsed/60:.1f} 分钟")
                print(f"平均速度: {avg_speed:.2f} 用户/秒")
                print("="*70)
                break

            # 检查是否卡住
            if current == last_current and current > 0:
                # 可能已完成或卡住
                pass

            last_current = current
            time.sleep(refresh_interval)

    except KeyboardInterrupt:
        print()
        print()
        print("⏹️  监控已停止")

        if last_current > 0:
            elapsed = time.time() - start_time
            avg_speed = last_current / elapsed
            print()
            print(f"已完成: {last_current:,}/{total:,}")
            print(f"平均速度: {avg_speed:.2f} 用户/秒")


if __name__ == "__main__":
    # 自动检测最新的日志文件
    log_files = [
        "batch_scrape_concurrent_10.log",
        "batch_scrape_concurrent_19.log",
        "batch_scrape_concurrent_8.log",
        "batch_scrape_concurrent_5.log",
        "batch_scrape_final.log",
    ]

    log_file = None
    for f in log_files:
        if Path(f).exists():
            log_file = f
            break

    if log_file:
        monitor_progress(log_file, refresh_interval=2)
    else:
        print("❌ 未找到日志文件")
        print("请指定日志文件路径:")
        print("  python3 monitor_progress_bar.py <log_file>")
