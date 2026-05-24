from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from pydantic import EmailStr, BaseModel
from fastapi import HTTPException
from fastapi_mail.errors import ConnectionErrors
from typing import List
import os
from dotenv import load_dotenv
load_dotenv()


class EmailSchema(BaseModel):
   email: List[EmailStr]

conf = ConnectionConfig(
   MAIL_USERNAME=os.getenv('MAIL_ID'),
   MAIL_FROM=os.getenv('MAIL_ID'),
   MAIL_PASSWORD=os.getenv('MAIL_APP_PASSWORD'),
   MAIL_PORT=587,
   MAIL_SERVER="smtp.gmail.com",
   MAIL_STARTTLS=True,
   MAIL_SSL_TLS=False,
   USE_CREDENTIALS=True
)


async def send_mail(subject: str, body, email: EmailSchema):
   try:
      message = MessageSchema(
           subject=subject,
           recipients=email.dict().get("email"),  # List of recipients, as many as you can pass 
           body=body,
           subtype="html"
      )

      fm = FastMail(conf)
      response = await fm.send_message(message)

      return response
   except ConnectionErrors as e:
      raise HTTPException(
         status_code=500,
         detail="Failed to connect to mail server"
      )

   except Exception as e:
      raise HTTPException(
         status_code=500,
         detail="Failed to send email"
      )