from fastapi import APIRouter, Depends, HTTPException, Response, Request, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime, timezone


from app.config import get_db
from app.services import crud
from app.services.crud import save_project, update_project, fetch_projects, delete_project
from app.schemas.user import APIResponse
from app.schemas.auth import TokenData
from app.schemas.project import ProjectBase, ProjectResponse
from app.utils import get_current_user

router = APIRouter()


@router.post("/add", response_model=APIResponse)
def add_project(body: ProjectBase, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_id = user.id

        # body.end_date = datetime.date(body.end_date)
        # body.start_date = datetime.date(body.start_date)

        if body.end_date and body.is_ongoing:
            raise HTTPException(
                400,
                "Project cannot have a end date if it is ongoing"
            )
        
        if body.end_date and body.end_date < body.start_date:
            raise HTTPException(
                400,
                "End date cannot be before start date"
            )
        
        db_project = save_project(body, user_id, db)

        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=True,
                message="Project Saved!",
                data=ProjectResponse.model_validate(db_project).model_dump()
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
    
    except IntegrityError as e:
        db.rollback()
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message=f"Cannot save project! Try again later: {str(e)}"
            ))
        )
    
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Unexpected Error Occurred"
            )),
            500
        )


@router.put("/update/{project_id}", response_model=APIResponse)
def Update_project(project_id: int, body: ProjectBase, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_id = user.id

        if body.end_date and body.is_ongoing:
            return HTTPException(
                400,
                "Project cannot have a end date if it is ongoing"
            )
        
        if body.end_date and body.end_date < body.start_date:
            return HTTPException(
                400,
                "End date cannot be before start date"
            )

        db_project = update_project(body, user_id, project_id, db)

        if not db_project:
            raise HTTPException(
                404,
                "Project not found"
            )
        
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=True,
                message="Project updated!",
                data=ProjectResponse.model_validate(db_project).model_dump()
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
    
    except IntegrityError as e:
        db.rollback()
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Cannot update project! Try again later"
            ))
        )
    
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Unexpected Error Occurred"
            )),
            500
        )


@router.get("/get-all", response_model=APIResponse)
def get_all_projects(user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try: 
        user_id = user.id

        projects = fetch_projects(user_id, db)

        if not projects:
            raise HTTPException(
                404,
                "No projects found"
            )
        
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=True,
                message="Projects fetched",
                data=[ProjectResponse.model_validate(project).model_dump() for project in projects]
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
    
    except IntegrityError as e:
        db.rollback()
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Cannot fetch projects Try again later"
            ))
        )
    
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Unexpected Error Occurred"
            )),
            500
        )


@router.delete("/delete/{project_id}", response_model=APIResponse)
def Delete_project(project_id:int, user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_id = user.id

        deleted = delete_project(project_id, user_id, db)

        if not deleted:
            raise HTTPException(
                404,
                "Project not found"
            )

        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=True,
                message="Project deleted",
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
    
    except IntegrityError as e:
        db.rollback()
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Cannot fetch projects Try again later"
            ))
        )
    
    except Exception as e:
        db.rollback()
        print(e)
        return JSONResponse(
            jsonable_encoder(APIResponse(
                success=False,
                message="Unexpected Error Occurred"
            )),
            500
        )



