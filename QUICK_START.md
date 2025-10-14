# 快速开始指南

## 步骤 1: 安装依赖

```bash
cd /Users/jiajun/tiktok_user_scrape
pip install -r requirements.txt
```

## 步骤 2: 配置 API Token

编辑 `config.py`，填入你的 API Token。

## 步骤 3: 准备用户列表

将要爬取的用户 URL 保存到文本文件（如 `data/users.txt`）。

## 步骤 4: 运行爬取

### 方法 1: 直接运行（前台）

```bash
python3 scripts/batch_scrape_to_csv_concurrent.py
```

### 方法 2: 后台运行

```bash
nohup python3 scripts/batch_scrape_to_csv_concurrent.py > logs/scrape.log 2>&1 &
```

## 步骤 5: 监控进度

```bash
python3 scripts/monitor_progress_bar.py
```

## 步骤 6: 处理失败用户

```bash
python3 scripts/retry_all_failed_users.py
```

## 步骤 7: 合并数据

```bash
python3 scripts/merge_csv_files.py
```
