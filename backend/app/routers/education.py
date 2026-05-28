from fastapi import APIRouter, Depends, HTTPException, Response, Request, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime, timezone


from app.config import get_db
from app.services import crud
from app.services.crud import upload_education, update_education, delete_education, get_education
from app.schemas.user import APIResponse
from app.schemas.auth import TokenData
from app.schemas.education import EducationResponse, EducationBase
from app.utils import get_current_user
from app.services.files import upload_avatar, delete_avatar

router = APIRouter()

@router.post("/add", response_model=APIResponse)
def add_education(data: EducationBase, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        print("Data: ", data)
        education = upload_education(db, data, user.id)

        return JSONResponse(
            status_code=201,
            content=jsonable_encoder(APIResponse(
                success=True,
                message="Education Added",
                data = EducationResponse.model_validate(education)
            ))
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=f"Unexpected Error Occured {str(e)}"
            ))
        )

@router.get("/get", response_model=APIResponse)
def get_educations(user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    educations = get_education(db, user.id)

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(APIResponse(
            success=True,
            message="Educations Fetched",
            data = [EducationResponse.model_validate(e) for e in educations]
        ))
    )

@router.put("/update/{education_id}", response_model=APIResponse)
def update_education(education_id: int, data: EducationBase,
user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try: 
        education = crud.update_education(db, data, education_id, user.id)

        if not education:
            return JSONResponse(
                status_code=404,
                content=jsonable_encoder(APIResponse(
                    success=False,
                    message=f"Education not found"
                ))
            )
        
        return JSONResponse(
            status_code=200,
            content = jsonable_encoder(APIResponse(
                success=True,
                message="Education Updated",
                data=EducationResponse.model_validate(education)
            ))
        )
        
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=f"Unexpected Error Occured {str(e)}"
            ))
        )


@router.delete("/delete/{education_id}", response_model=APIResponse)
def delete_education(education_id: int, user: TokenData = Depends(get_current_user),
db: Session = Depends(get_db)):
    try:
        deleted = crud.delete_education(db, education_id, user.id)

        if not deleted:
            return JSONResponse(
            status_code=404,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=f"Education not found"
            ))
            )
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(APIResponse(
                success=True,
                message="Education Deleted"
            )))
    except Exception:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(APIResponse(
                success=False,
                message=f"Unexpected Error Occured {str(e)}"
            ))
        )