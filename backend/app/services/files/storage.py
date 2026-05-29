from app.config.Supabase import supabase
from dotenv import load_dotenv
import os
load_dotenv()

def get_signed_upload_url(bucket: str, file: str) -> str:
    response = supabase.storage.from_(bucket).create_signed_upload_url(file)

    return response["signed_url"]

def confirm_upload_url(bucket: str, file: str):
    folder = file.split("/",1)[1].rsplit("/", 1)[0]
    file_name = file.split("/",1)[1].rsplit("/", 1)[1]
    response = supabase.storage.from_(bucket).list(folder)

    for item in response:
        print("\n\n ITEM: ", item)
        if item["name"] == file_name:
            return True

    return False

