#!/usr/bin/env python3
"""
TikTok User Profile Scraper - TikHub API
使用 TikHub API v3 handler_user_profile 接口爬取用户资料
API 文档: https://api.tikhub.io/
"""

import asyncio
import json
import httpx
from datetime import datetime
from pathlib import Path


class TikHubUserScraper:
    """TikHub TikTok 用户资料爬虫"""

    def __init__(self, api_token: str, base_url: str = "https://api.tikhub.io"):
        """
        初始化爬虫

        Args:
            api_token: TikHub API Token
            base_url: API 服务器地址
                - 国际用户: https://api.tikhub.io
                - 中国大陆用户: https://api.tikhub.dev
        """
        self.base_url = base_url
        self.api_token = api_token
        self.api_endpoint = f"{base_url}/api/v1/tiktok/app/v3/handler_user_profile"

    async def fetch_user_profile(
        self,
        unique_id: str = "",
        sec_user_id: str = "",
        user_id: str = ""
    ) -> dict:
        """
        获取用户资料

        Args:
            unique_id: TikTok 用户名（推荐使用），例如 "tiktok" 或 ".chrrvxsz"
            sec_user_id: TikTok 用户 sec_user_id（速度最快）
            user_id: TikTok 用户 uid（纯数字）

        注意：
            - 至少提供一个参数
            - 优先级：sec_user_id > user_id > unique_id
            - 优先级越高速度越快

        Returns:
            用户资料数据字典，失败返回 None
        """
        if not any([unique_id, sec_user_id, user_id]):
            print("✗ 错误：至少需要提供 unique_id、sec_user_id 或 user_id 中的一个")
            return None

        # 显示使用的参数
        params_display = []
        if sec_user_id:
            params_display.append(f"sec_user_id={sec_user_id[:20]}...")
        if user_id:
            params_display.append(f"user_id={user_id}")
        if unique_id:
            params_display.append(f"unique_id=@{unique_id}")

        print(f"正在获取用户资料: {', '.join(params_display)}")

        # 构建请求头（使用 Bearer Token 认证）
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }

        # 构建请求参数
        params = {
            "unique_id": unique_id if unique_id else "",
            "sec_user_id": sec_user_id if sec_user_id else "",
            "user_id": user_id if user_id else ""
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(
                    self.api_endpoint,
                    params=params,
                    headers=headers
                )

                print(f"请求 URL: {response.url}")
                print(f"响应状态码: {response.status_code}")

                response.raise_for_status()

                data = response.json()

                if data.get("code") == 200:
                    print(f"✓ 成功获取用户资料")
                    return data
                else:
                    print(f"✗ API 返回错误 (code={data.get('code')}): {data.get('message', 'Unknown error')}")
                    return None

            except httpx.HTTPStatusError as e:
                print(f"✗ HTTP 状态错误: {e.response.status_code}")
                try:
                    error_data = e.response.json()
                    print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"响应内容: {e.response.text[:500]}")
                return None
            except httpx.HTTPError as e:
                print(f"✗ HTTP 请求错误: {e}")
                return None
            except Exception as e:
                print(f"✗ 未知错误: {e}")
                return None

    async def scrape_user(self, username: str, save_to_file: bool = True) -> dict:
        """
        爬取指定用户名的资料

        Args:
            username: TikTok 用户名（不含 @ 符号）
            save_to_file: 是否保存到文件

        Returns:
            用户资料数据
        """
        # 移除 @ 符号（如果有）
        if username.startswith("@"):
            username = username[1:]

        # 获取用户资料（使用 unique_id）
        result = await self.fetch_user_profile(unique_id=username)

        if result and save_to_file:
            # 保存到文件
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"{username}_{timestamp}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"✓ 数据已保存到: {filename}")

        return result

    def print_user_summary(self, data: dict):
        """打印用户资料摘要"""
        if not data:
            print("无法打印用户资料摘要：数据为空")
            return

        print("\n" + "="*60)
        print("用户资料摘要")
        print("="*60)

        # 根据 TikHub API 返回的数据结构提取信息
        # TikHub API 返回格式：
        # {
        #   "code": 200,
        #   "message": "success",
        #   "data": {
        #     "user": { ... },
        #     "stats": { ... }
        #   }
        # }

        # 提取用户信息
        if "data" in data:
            api_data = data["data"]
            user_info = api_data.get("user", {})

            # 显示用户信息
            if user_info:
                print(f"用户 ID (UID): {user_info.get('uid', 'N/A')}")
                print(f"用户名 (unique_id): {user_info.get('unique_id', 'N/A')}")
                print(f"昵称 (nickname): {user_info.get('nickname', 'N/A')}")
                print(f"Sec User ID: {user_info.get('sec_uid', 'N/A')[:50]}...")

                # 签名（可能包含换行符）
                signature = user_info.get('signature', 'N/A')
                if signature and len(signature) > 100:
                    signature = signature[:100] + "..."
                print(f"签名: {signature}")

                # 验证状态
                verification_type = user_info.get('verification_type', 0)
                verified_status = "已验证" if verification_type > 0 else "未验证"
                print(f"验证状态: {verified_status}")

                # 统计数据（直接从 user 对象中获取）
                print(f"\n统计数据:")
                print(f"  关注数: {user_info.get('following_count', 0):,}")
                print(f"  粉丝数: {user_info.get('follower_count', 0):,}")
                print(f"  获赞总数: {user_info.get('total_favorited', 0):,}")
                print(f"  视频数: {user_info.get('aweme_count', 0):,}")
                print(f"  可见视频数: {user_info.get('visible_videos_count', 0):,}")

                # 其他信息
                print(f"\n其他信息:")
                if user_info.get('ins_id'):
                    print(f"  Instagram: {user_info.get('ins_id')}")
                if user_info.get('youtube_channel_title'):
                    print(f"  YouTube: {user_info.get('youtube_channel_title')}")
                if user_info.get('twitter_name'):
                    print(f"  Twitter: {user_info.get('twitter_name')}")
            else:
                print("未找到用户信息")
        else:
            print("无法解析用户信息，数据结构不符合预期")

        print("="*60 + "\n")


async def main():
    """主函数"""
    print("="*60)
    print("TikHub TikTok 用户资料爬虫")
    print("="*60)
    print()

    # 配置
    # 从 config.py 导入配置
    try:
        import config
        API_BASE_URL = config.API_BASE_URL
        API_TOKEN = config.API_TOKEN
        TARGET_USERNAME = config.TARGET_USERS[0] if config.TARGET_USERS else ".chrrvxsz"
    except ImportError:
        # 如果没有 config.py，使用默认配置
        API_BASE_URL = "https://api.tikhub.io"
        API_TOKEN = "YOUR_API_TOKEN_HERE"
        TARGET_USERNAME = ".chrrvxsz"

    print(f"API 地址: {API_BASE_URL}")
    print(f"API Token: {API_TOKEN[:20]}...")
    print(f"目标用户: @{TARGET_USERNAME}")
    print()

    # 创建爬虫实例
    scraper = TikHubUserScraper(
        api_token=API_TOKEN,
        base_url=API_BASE_URL
    )

    # 爬取用户资料
    result = await scraper.scrape_user(TARGET_USERNAME)

    if result:
        # 打印摘要
        scraper.print_user_summary(result)
        print("✓ 爬取完成！")
    else:
        print("✗ 爬取失败！")


if __name__ == "__main__":
    asyncio.run(main())
