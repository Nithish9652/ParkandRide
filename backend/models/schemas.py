from pydantic import BaseModel, EmailStr
from datetime import datetime

# ——— Auth ———
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str

class UserProfile(BaseModel):
    userId: EmailStr
    loyaltyPoints: int

# ——— Booking requests ———
class BookingRequest(BaseModel):
    start: datetime
    hours: int
    days: int
    months: int
    plate: str

class CancelRequest(BaseModel):
    row: int
    col: int
    start: datetime
    end: datetime
    plate: str

# ——— Booking responses ———
class Slot(BaseModel):
    row: int
    col: int

class SlotResponse(BaseModel):
    slot: Slot
    start: datetime
    end: datetime
    qr: str

class SimpleMessage(BaseModel):
    message: str

class SlotOnly(BaseModel):
    slot: Slot

class SlotOccupiedStatus(BaseModel):
    occupied: bool

# ——— Occupancy / Availability ———
class OccupancyStatus(BaseModel):
    occupied: int
    total: int

class FreeSlotsStatus(BaseModel):
    free: int
    total: int
