from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import SessionLocal, User
from ..auth import get_current_user
from ..config import Config
import stripe
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/payments", tags=["payments"])

stripe.api_key = Config.STRIPE_SECRET_KEY

class SubscriptionCreate(BaseModel):
    price_id: str  # Monthly or yearly

class SubscriptionResponse(BaseModel):
    client_secret: Optional[str] = None
    subscription_id: Optional[str] = None
    status: str

@router.post("/create-subscription")
async def create_subscription(
    request: SubscriptionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Создает подписку Stripe для пользователя.
    """
    try:
        # Получаем или создаем customer
        db = SessionLocal()
        user = db.query(User).filter(User.id == current_user.id).first()
        
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.id,
                metadata={"user_id": current_user.id}
            )
            user.stripe_customer_id = customer.id
            db.commit()
        else:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)
        
        # Создаем подписку
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": request.price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
            metadata={"user_id": current_user.id}
        )
        
        db.close()
        
        return SubscriptionResponse(
            client_secret=subscription.latest_invoice.payment_intent.client_secret,
            subscription_id=subscription.id,
            status=subscription.status
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Webhook для обработки событий Stripe.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Обрабатываем события
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_session(session)
    elif event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        await handle_invoice_paid(invoice)
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await handle_subscription_deleted(subscription)
    
    return {"status": "success"}

async def handle_checkout_session(session):
    """Обработка успешной оплаты"""
    user_id = session.get("metadata", {}).get("user_id")
    if not user_id:
        return
    
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.subscription_status = "active"
        user.subscription_end = datetime.utcnow() + timedelta(days=30)
        db.commit()
    db.close()

async def handle_invoice_paid(invoice):
    """Обновление статуса подписки при оплате"""
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return
    
    db = SessionLocal()
    # Ищем пользователя по subscription_id
    user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
    if user:
        user.subscription_status = "active"
        user.subscription_end = datetime.utcnow() + timedelta(days=30)
        db.commit()
    db.close()

async def handle_subscription_deleted(subscription):
    """Отмена подписки"""
    user_id = subscription.get("metadata", {}).get("user_id")
    if not user_id:
        return
    
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.subscription_status = "inactive"
        user.subscription_end = None
        db.commit()
    db.close()

@router.get("/prices")
async def get_prices():
    """
    Возвращает список доступных цен.
    """
    return {
        "monthly": {
            "id": Config.PRICE_MONTHLY,
            "amount": 10,
            "currency": "usd",
            "interval": "month",
            "name": "Monthly"
        },
        "yearly": {
            "id": Config.PRICE_YEARLY,
            "amount": 96,
            "currency": "usd",
            "interval": "year",
            "name": "Yearly (20% off)"
        },
        "one_time": {
            "id": Config.PRICE_ONE_TIME,
            "amount": 50,
            "currency": "usd",
            "interval": "one_time",
            "name": "One-time access"
        }
    }

@router.get("/status")
async def get_subscription_status(current_user: User = Depends(get_current_user)):
    """
    Возвращает статус подписки текущего пользователя.
    """
    db = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()
    db.close()
    
    is_active = user and user.subscription_status == "active"
    end_date = user.subscription_end if user else None
    
    return {
        "is_active": is_active,
        "end_date": end_date.isoformat() if end_date else None,
        "plan": user.plan if user else None
    }

@router.post("/cancel")
async def cancel_subscription(current_user: User = Depends(get_current_user)):
    """
    Отменяет подписку.
    """
    db = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user or not user.stripe_subscription_id:
        db.close()
        raise HTTPException(status_code=400, detail="No active subscription")
    
    try:
        stripe.Subscription.modify(
            user.stripe_subscription_id,
            cancel_at_period_end=True
        )
        user.subscription_status = "canceling"
        db.commit()
        db.close()
        return {"status": "canceling_at_period_end"}
    except Exception as e:
        db.close()
        raise HTTPException(status_code=400, detail=str(e))
