import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.middlewares.rate_limit import check_rate
from src.schemas.box import BoxCreateResponse
from src.services.box_service import create_box
from src.services.user_service import get_user_by_token

logger = logging.getLogger(__name__)

_db_dependency = Depends(get_db)

router = APIRouter()


@router.post(
    "/box",
    response_model=BoxCreateResponse,
    status_code=status.HTTP_200_OK,
    summary="Создать новый box",
    description="Создает новый ящик отзывов и возвращает UUID и owner_token."
)
def create_box_endpoint(
    request: Request,
    authorization: str = Header(None, alias="Authorization"),
    db: Session = _db_dependency,
):
    """Создает новый box. Если предоставлен Authorization Bearer токен, связывает box с пользователем."""
    logger.info("Create box request from %s", request.client.host)
    check_rate(request.client.host, "POST:/box")
    user_id = None
    if authorization:
        token = authorization
        if token.lower().startswith("bearer "):
            token = token[7:].strip()
        user = get_user_by_token(db, token)
        if user:
            user_id = user.id
            logger.info("Authenticated user %s is creating a box", user.username)
    try:
        box = create_box(db, user_id=user_id)
    except Exception as exc:
        logger.critical("Failed to create box", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create box",
        ) from exc
    logger.info("Box created: uuid=%s", box.uuid)
    return box
