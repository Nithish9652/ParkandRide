from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from auth.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from models.schemas import UserRegister, UserLogin, TokenResponse, UserProfile
from utils.mongo import db  # MongoDB connection

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Dependency to extract and verify JWT
def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return email
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/register")
async def register(user: UserRegister):
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user.password)
    await db["users"].insert_one({
        "email": user.email,
        "hashed_password": hashed_password
    })
    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    existing_user = await db["users"].find_one({"email": user.email})
    if not existing_user or not verify_password(user.password, existing_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token}


@router.get("/me", response_model=UserProfile)
async def read_profile(email: str = Depends(get_current_user_email)):
    """
    Returns the current user's profile.
    Loyalty points are stubbed to 0 for now; replace with real data lookup as needed.
    """
    # Optionally fetch more data from DB here
    return UserProfile(userId=email, loyaltyPoints=0)
