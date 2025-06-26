from fastapi import FastAPI, Depends, HTTPException, Request, Header
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError
from datetime import datetime
from dotenv import load_dotenv
import os
import stripe

# --- Load env and configure Stripe ---
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# --- Import your routers & utilities ---
from auth.routes import router as auth_router
from auth.auth_utils import decode_access_token
from routes.payments import router as payments_router  # ← payments routes
from models.schemas import (
    BookingRequest,
    CancelRequest,
    SlotResponse,
    SimpleMessage,
    SlotOnly,
    SlotOccupiedStatus,
    OccupancyStatus,
    FreeSlotsStatus,
)
from services.booking_service import service, BookingError

# --- App setup ---
app = FastAPI()

# CORS setup (open for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes (login/register)
app.include_router(auth_router)

# Include payments routes at /payments
app.include_router(payments_router, prefix="/payments", tags=["payments"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT decode dependency
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        if not payload or "sub" not in payload:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# --- Booking endpoints ---

@app.post("/book", response_model=SlotResponse)
def book(req: BookingRequest, user: str = Depends(get_current_user)):
    try:
        slot, start_dt, end_dt, qr = service.book(
            req.start, req.hours, req.days, req.months, req.plate
        )
        return {
            "slot": {"row": slot[0], "col": slot[1]},
            "start": start_dt,
            "end": end_dt,
            "qr": qr
        }
    except BookingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/cancel", response_model=SimpleMessage)
def cancel(req: CancelRequest, user: str = Depends(get_current_user)):
    try:
        service.cancel(req.row, req.col, req.start, req.end, req.plate)
        return {"message": "Cancelled successfully"}
    except BookingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/occupancy", response_model=OccupancyStatus)
def occupancy(at: datetime, user: str = Depends(get_current_user)):
    occupied = service.occupancy_at(at)
    total = service.TOTAL
    return {"occupied": occupied, "total": total}

@app.get("/slot-occupied", response_model=SlotOccupiedStatus)
def slot_occupied(slot: str, at: datetime, user: str = Depends(get_current_user)):
    return {"occupied": service.is_slot_occupied(slot, at)}

@app.post("/find-slot", response_model=SlotOnly)
def find_slot(start: datetime, end: datetime, user: str = Depends(get_current_user)):
    slot = service.find_slot(start, end)
    if slot:
        return {"slot": {"row": slot[0], "col": slot[1]}}
    raise HTTPException(status_code=404, detail="No available slot")

@app.get("/free-slots", response_model=FreeSlotsStatus)
def free_slots(at: datetime, user: str = Depends(get_current_user)):
    occupied = service.occupancy_at(at)
    total = service.TOTAL
    return {"free": total - occupied, "total": total}
