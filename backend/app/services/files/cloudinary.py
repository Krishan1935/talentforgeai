import cloudinary.uploader
from dotenv import load_dotenv
import os
load_dotenv()

AVATAR_FOLDER = os.getenv("CLOUDINARY_AVATARS")
def upload_avatar(file, user_id: int) -> str:
    result = cloudinary.uploader.upload(
        file,
        folder=AVATAR_FOLDER,
        public_id=f"user_{user_id}",
        overwrite=True,                    # replaces old avatar automatically
        transformation=[
            {"width": 400, "height": 400, "crop": "fill", "gravity": "face"}
        ]
    )
    return result["secure_url"]

def delete_avatar(user_id: int):
    cloudinary.uploader.destroy(f"{AVATAR_FOLDER}/user_{user_id}")