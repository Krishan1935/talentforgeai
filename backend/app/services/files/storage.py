from app.config.Supabase import supabase
from dotenv import load_dotenv
import os
load_dotenv()

def get_signed_upload_url(bucket: str, file: str) -> str:
    response = supabase.storage.from_(bucket).create_signed_upload_url(file)

    return response["signed_url"]