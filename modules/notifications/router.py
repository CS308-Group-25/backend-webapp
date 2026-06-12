from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.model import User
from modules.notifications.repository import NotificationRepository

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=list[NotificationResponse])
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = NotificationRepository(db)
    items = repo.get_unread(current_user.id)
    return [
        NotificationResponse(
            id=n.id,
            message=n.message,
            is_read=n.is_read,
            created_at=n.created_at.isoformat(),
        )
        for n in items
    ]


@router.patch("/read-all", status_code=204)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = NotificationRepository(db)
    repo.mark_all_read(current_user.id)
    db.commit()


@router.patch("/{notification_id}/read", status_code=204)
def mark_single_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = NotificationRepository(db)
    if not repo.mark_single_read(notification_id, current_user.id):
        raise HTTPException(status_code=404, detail="Notification not found")
    db.commit()


@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = NotificationRepository(db)
    if not repo.delete_by_id(notification_id, current_user.id):
        raise HTTPException(status_code=404, detail="Notification not found")
    db.commit()
