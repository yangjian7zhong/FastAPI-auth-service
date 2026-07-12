import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.path.join(BASE_DIR, "test.db")

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACTIVATION_TOKEN_EXPIRE_MINUTES: int = 10
    MAIL_HOST: str = os.getenv("MAIL_HOST", "smtp.163.com")
    MAIL_PORT: int = 465
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    BASE_URL: str = os.getenv("BASE_URL", "https://fastapi-auth-service-production-87f3.up.railway.app")
    ENV: str = os.getenv("ENV", "dev")
    ENABLE_DEMO_ACCOUNT: bool = os.getenv("ENABLE_DEMO_ACCOUNT", "false").lower() == "true"
    # 在 Settings 类中添加
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # Redis 配置（支持从环境变量读取，没有则用默认值）
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")  # 如果有密码

settings = Settings()
