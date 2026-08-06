import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
    # По умолчанию используем SQLite, если не указана DATABASE_URL
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./synapse.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
