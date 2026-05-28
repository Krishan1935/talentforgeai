import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os
load_dotenv()

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

cloudinary.config(
    cloud_name = CLOUD_NAME,
    api_key = API_KEY,
    api_secret = API_SECRET
)