import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./synapse.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    ALGORITHM = "HS256"

# Создаём экземпляр для импорта
settings = Config()
