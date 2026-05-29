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
        if item["name"] == file_name:
            return True

    return False

def get_signed_view_url(bucket: str, file: str, expires_in: int):
    try:
        file_name = file.split("/",1)[1].rsplit("/", 0)[0]
        response = supabase.storage\
            .from_(bucket).create_signed_url(file_name, expires_in)

        return response["signedUrl"]
    except:
        return None

def remove_file(bucket: str, paths: [str]):
    try:
        paths = [path.split("/",1)[1].rsplit("/", 0)[0] for path in paths]
        response = supabase.storage\
            .from_(bucket).remove(paths)
        
        return response
    except Exception as e:
        print(e)
        return None
