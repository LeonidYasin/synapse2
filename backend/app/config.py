import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./synapse.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    
    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Цены в центах (USD)
    PRICE_MONTHLY = 1000  # $10
    PRICE_YEARLY = 9600   # $96 ($8/мес)
    PRICE_ONE_TIME = 5000 # $50 (разовый доступ)
