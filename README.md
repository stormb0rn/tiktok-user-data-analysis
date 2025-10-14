# TikTok User Data Analysis

一个高效的 TikTok 用户数据分析工具，使用 TikHub API 批量获取和分析用户资料信息。

## 📊 项目特点

- ✅ **高并发爬取**: 使用 asyncio 实现并发请求，速度提升 10 倍
- ✅ **自动重试**: 失败用户自动重试机制
- ✅ **进度监控**: 实时显示爬取进度和速度
- ✅ **数据去重**: 自动合并和去重用户数据
- ✅ **高成功率**: 最终成功率达 99.9%

## 📁 项目结构

```
tiktok_user_scrape/
├── scripts/              # 核心脚本
│   ├── scrape_user_tikhub.py              # TikHub API 封装
│   ├── batch_scrape_to_csv_concurrent.py  # 批量并发爬取
│   ├── retry_all_failed_users.py          # 重试失败用户
│   ├── merge_csv_files.py                 # 合并 CSV 文件
│   ├── monitor_progress_bar.py            # 进度监控
│   └── utils/                             # 辅助工具
├── data/                 # 数据文件
│   ├── Nova 01 User list
│   ├── Nova 02 User List
│   └── failed_users*.txt
├── output/              # 输出结果
│   ├── nova01_users.csv
│   ├── nova02_users.csv
│   └── merged_all_users.csv
├── logs/                # 日志文件
├── archive/             # 历史版本
├── config.py            # 配置文件
├── requirements.txt     # 依赖包
└── README.md           # 项目文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Token

编辑 `config.py` 文件，填入你的 TikHub API Token：

```python
API_TOKEN = "your_api_token_here"
API_BASE_URL = "https://api.tikhub.io"
CONCURRENCY = 10  # 并发数
```

### 3. 准备用户列表

创建一个文本文件，每行一个 TikTok 用户 URL：

```
https://www.tiktok.com/@username1
https://www.tiktok.com/@username2
https://www.tiktok.com/@username3
```

### 4. 开始爬取

```bash
# 修改脚本中的路径配置
python3 scripts/batch_scrape_to_csv_concurrent.py
```

## 📖 使用指南

### 批量爬取用户

```python
from scripts.scrape_user_tikhub import TikHubUserScraper

# 创建爬虫实例
scraper = TikHubUserScraper(
    api_token="your_token",
    base_url="https://api.tikhub.io"
)

# 获取单个用户
result = await scraper.fetch_user_profile(unique_id="username")
```

### 重试失败用户

```bash
python3 scripts/retry_all_failed_users.py
```

### 合并多个 CSV

```bash
python3 scripts/merge_csv_files.py
```

### 监控爬取进度

```bash
python3 scripts/monitor_progress_bar.py
```

## 📊 数据字段

输出 CSV 包含 21 个字段：

| 字段 | 说明 |
|------|------|
| username | 用户名 |
| unique_id | 唯一 ID |
| nickname | 昵称 |
| uid | 用户 ID |
| sec_uid | 安全 ID |
| signature | 个人简介 |
| follower_count | 粉丝数 |
| following_count | 关注数 |
| total_favorited | 获赞总数 |
| aweme_count | 作品数 |
| visible_videos_count | 可见视频数 |
| verification_type | 认证类型 |
| verified | 是否认证 |
| bio_email | 邮箱 |
| category | 分类 |
| account_type | 账号类型 |
| avatar_larger_url | 头像 URL |
| profile_url | 主页 URL |
| scrape_time | 爬取时间 |
| scrape_status | 爬取状态 |
| error_message | 错误信息 |

## 🎯 项目成果

本项目成功爬取：

- **总用户数**: 9,490 个唯一用户
- **成功率**: 99.9%
- **Nova 01**: 5,335/5,339 (99.9%)
- **Nova 02**: 4,172/4,177 (99.9%)
- **合并数据**: 9,481 成功，9 失败

## ⚙️ 配置说明

### 并发数调优

- **推荐值**: 10 (平衡速度和稳定性)
- **保守值**: 5 (更稳定，速度较慢)
- **激进值**: 15-19 (可能触发限流)

### API 限制

- QPS 限制：根据套餐不同 (10-20 请求/秒)
- 建议并发数不超过 QPS 限制

## 🔧 故障排除

### 429 错误 (Too Many Requests)

**问题**: 请求过快触发限流

**解决**: 降低并发数 (CONCURRENCY)

### 连接超时

**问题**: 网络不稳定

**解决**:
1. 检查网络连接
2. 增加超时时间 (timeout=60.0)
3. 使用代理

### 部分用户失败

**问题**: 账号已删除/私密/不存在

**解决**: 运行重试脚本，仍然失败的账号可忽略

## 📝 开发日志

- **2025-10-14**: 初始版本，实现基础爬取功能
- **2025-10-14**: 优化并发性能，速度提升 10 倍
- **2025-10-14**: 添加重试机制，成功率提升至 99.9%
- **2025-10-14**: 实现数据合并和去重功能

## 📄 许可证

本项目仅供学习和研究使用。使用时请遵守：

1. TikTok 服务条款
2. TikHub API 使用协议
3. 相关法律法规

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题，请提交 Issue。

---

**注意**: 请合理使用 API，避免过度请求。爬取的数据仅供个人研究使用。
