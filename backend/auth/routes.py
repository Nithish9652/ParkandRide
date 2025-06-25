from fastapi import APIRouter, HTTPException
from models.schemas import UserRegister, UserLogin, TokenResponse
from auth.auth_utils import hash_password, verify_password, create_access_token
from utils.mongo import db  # MongoDB connection

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(user: UserRegister):
    # Check if user already exists
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash password and store user
    hashed_password = hash_password(user.password)
    await db["users"].insert_one({
        "email": user.email,
        "hashed_password": hashed_password
    })
    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    # Find user by email
    existing_user = await db["users"].find_one({"email": user.email})
    if not existing_user or not verify_password(user.password, existing_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Generate access token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token}
