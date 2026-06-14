import logging

from sqlalchemy.orm import Session

from src.models.box import Box
from src.utils.security import generate_token, generate_uuid

logger = logging.getLogger(__name__)


def create_box(db: Session, user_id: int | None = None) -> Box:
    box = Box(
        uuid=generate_uuid(),
        owner_token=generate_token(),
        user_id=user_id,
    )
    db.add(box)
    try:
        db.commit()
        db.refresh(box)
        logger.info("Created box uuid=%s user_id=%s", box.uuid, user_id)
        return box
    except Exception as exc:
        db.rollback()
        logger.critical("Database failure while creating box user_id=%s", user_id, exc_info=exc)
        raise
