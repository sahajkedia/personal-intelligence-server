from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
