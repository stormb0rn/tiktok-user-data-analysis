# TikTok User Scraper 配置文件示例

# API 配置
API_BASE_URL = "https://api.tikhub.io"  # TikHub API 地址
API_TOKEN = "your_api_token_here"       # 替换为你的 API Token

# 爬取配置
CONCURRENCY = 10          # 并发数（推荐 10）
REQUEST_TIMEOUT = 60.0    # 请求超时时间（秒）
RETRY_DELAY = 1.0         # 重试延迟（秒）

# 文件路径配置
INPUT_USER_LIST = "data/users.txt"       # 输入用户列表
OUTPUT_CSV = "output/users.csv"           # 输出 CSV 文件
LOG_FILE = "logs/scrape.log"              # 日志文件

# 数据库配置（可选）
# DATABASE_URL = "sqlite:///data/users.db"
