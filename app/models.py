from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String, default="created")
    message: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AgendaItem(Base):
    __tablename__ = "agenda_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, unique=True)
    title: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    documents: Mapped[list["Document"]] = relationship(back_populates="agenda_item", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    __table_args__ = (
        UniqueConstraint(
            "agenda_item_id",
            "filename",
            name="uq_document_filename"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agenda_item_id: Mapped[int] = mapped_column(ForeignKey("agenda_items.id"))
    filename: Mapped[str] = mapped_column(String)
    storage_path: Mapped[str] = mapped_column(String)
    downloaded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    agenda_item: Mapped["AgendaItem"] = relationship(back_populates="documents")
