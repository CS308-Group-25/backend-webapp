from sqlalchemy.orm import Session

from modules.notifications.model import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, message: str) -> Notification:
        notif = Notification(user_id=user_id, message=message)
        self.db.add(notif)
        return notif

    def get_unread(self, user_id: int) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
            .order_by(Notification.created_at.desc())
            .all()
        )

    def mark_all_read(self, user_id: int) -> None:
        self.db.query(Notification).filter(
            Notification.user_id == user_id, Notification.is_read == False  # noqa: E712
        ).update({"is_read": True})

    def mark_single_read(self, notification_id: int, user_id: int) -> bool:
        updated = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .update({"is_read": True})
        )
        return updated > 0

    def delete_by_id(self, notification_id: int, user_id: int) -> bool:
        deleted = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .delete()
        )
        return deleted > 0
