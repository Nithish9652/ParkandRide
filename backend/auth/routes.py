from fastapi import APIRouter, HTTPException
from models.schemas import UserRegister, UserLogin, TokenResponse
from auth.auth_utils import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# Simulated in-memory user storage
user_db = {}

@router.post("/register")
def register(user: UserRegister):
    if user.email in user_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = hash_password(user.password)
    user_db[user.email] = hashed_password
    return {"message": "User registered successfully"}

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    stored_password = user_db.get(user.email)
    if not stored_password or not verify_password(user.password, stored_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token}
