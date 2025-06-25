from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = getenv("MONGO_URI")  # put this in your .env file
client = AsyncIOMotorClient(MONGO_URI)
db = client["park_and_ride"]
