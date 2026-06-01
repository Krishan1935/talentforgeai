from fastapi import APIRouter, Response, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from datetime import datetime, date, UTC

from app.config import get_db
from app.utils.dependencies import get_current_user
from app.schemas.experience import ExperienceBase, ExperienceResponse
from app.schemas.user import APIResponse
from app.schemas.auth import TokenData
from app.services.crud import (save_experience,
update_experience, fetch_experiences, delete_experience)

router = APIRouter()

@router.post("/add", response_model=APIResponse)
def add_experience(body: ExperienceBase, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_id = user.id

        if body.end_date and body.is_present:
            raise HTTPException(
                400,
                "Present experiences cannot have end date"
            )
        
        if body.end_date and body.end_date < body.start_date:
            raise HTTPException(
                400,
                "End date cannot be before start date"
            )

        db_exp = save_experience(body, user_id, db)

        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=True,
                message="Experience added succesfully",
                data = ExperienceResponse.model_validate(db_exp).model_dump()
            ))
        )

    except HTTPException as e:
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message=e.detail
            )),
            e.status_code
        )
    
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Cannot save experience! Try again later"
            )),
            500
        )
    
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Unexpected Error Ocurred"
            )),
            500
        )


@router.put("/update/{exp_id}", response_model=APIResponse)
def update_exp(exp_id: int, body: ExperienceBase, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_id = user.id

        if body.end_date and body.is_present:
            raise HTTPException(
                400,
                "Present experience cananot have end date"
            )
        
        if body.end_date and body.end_date < body.start_date:
            raise HTTPException(
                400,
                "End date cannot be before start date"
            )

        updated = update_experience(body, exp_id, user_id, db)

        if not updated:
            raise HTTPException(
                404,
                "Experience not found"
            )

        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=True,
                message="Experience updated",
                data = ExperienceResponse.model_validate(updated).model_dump()
            ))
        )

    except HTTPException as e:
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message=e.detail
            )),
            e.status_code
        )
    
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Cannot update experience! Try again later"
            )),
            500
        )
    
    except Exception as e:
        print(e)
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Unexpected Error Ocurred"
            )),
            500
        )


@router.delete("/delete/{exp_id}", response_model=APIResponse)
def delete_exp(exp_id: int, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_id = user.id

        deleted = delete_experience(exp_id, user_id, db)
        
        if not deleted:
            raise HTTPException(
                404,
                "Cannot find experience"
            )
        
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=True,
                message="Experience deleted succesfully",
                data=deleted
            ))
        )

    except HTTPException as e:
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message=e.detail
            )),
            e.status_code
        )
    
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Cannot delete experience! Try again later"
            )),
            500
        )
    
    except Exception as e:
        print(e)

        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Unexpected Error Ocurred"
            )),
            500
        )


@router.get("/get-all", response_model=APIResponse)
def get_experiences(user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        experiences = fetch_experiences(user.id, db)

        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=True,
                message="Experiences fetched",
                data=[ExperienceResponse.model_validate(exp).model_dump() for exp in experiences]
            ))
        )

    except HTTPException as e:
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message=e.detail
            )),
            e.status_code
        )
    
    except IntegrityError:
        db.rollback()
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Cannot fetch experiences! Try again later"
            )),
            500
        )
    
    except Exception as e:
        print(e)

        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Unexpected Error Ocurred"
            )),
            500
        )




