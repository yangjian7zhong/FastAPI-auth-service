import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = os.path.join(BASE_DIR, "test.db")

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
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
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    ENV: str = os.getenv("ENV", "dev")
    # 是否启用演示账号（默认关闭）
    ENABLE_DEMO_ACCOUNT: bool = os.getenv("ENABLE_DEMO_ACCOUNT", "false").lower() == "true"

settings = Settings()
