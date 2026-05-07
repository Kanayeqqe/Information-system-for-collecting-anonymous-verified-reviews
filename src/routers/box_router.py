from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.middlewares.rate_limit import check_rate
from src.schemas.box import BoxCreateResponse
from src.services.box_service import create_box

router = APIRouter()

@router.post("/box", response_model=BoxCreateResponse, status_code=status.HTTP_200_OK)
def create_box_endpoint(request: Request, db: Session = Depends(get_db)):
    check_rate(request.client.host, "POST:/box")
    box = create_box(db)
    if not box:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to create box")
    return box