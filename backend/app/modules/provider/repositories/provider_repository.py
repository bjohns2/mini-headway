from sqlalchemy.orm import Session

from app.modules.provider.models.provider import Provider


def get(db: Session, provider_id: int) -> Provider | None:
    return db.get(Provider, provider_id)
