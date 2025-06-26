from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe
import os

# Stripe is already configured in main.py, but safe to re-import here:
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter()

class CreateIntentReq(BaseModel):
    amount_cents: int
    currency: str = "usd"
    metadata: dict = None

class CreateIntentResp(BaseModel):
    client_secret: str

@router.post("/create-intent", response_model=CreateIntentResp)
def create_intent(req: CreateIntentReq):
    try:
        intent = stripe.PaymentIntent.create(
            amount=req.amount_cents,
            currency=req.currency,
            metadata=req.metadata or {}
        )
        return {"client_secret": intent.client_secret}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=e.user_message or str(e))

class ConfirmReq(BaseModel):
    payment_intent_id: str
    booking_id: str

@router.post("/confirm")
def confirm_payment(req: ConfirmReq):
    try:
        intent = stripe.PaymentIntent.retrieve(req.payment_intent_id)
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=e.user_message or str(e))

    if intent.status != "succeeded":
        raise HTTPException(status_code=400, detail="Payment not succeeded")
    # TODO: persist payment to your DB here, linking intent.id → req.booking_id
    return {"status": "ok"}
