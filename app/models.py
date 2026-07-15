from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    status: Mapped[str] = mapped_column(
        String,
        default="created"
    )

    message: Mapped[str] = mapped_column(
        String,
        default=""
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
