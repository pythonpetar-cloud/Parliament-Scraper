from sqlalchemy.orm import Session
from app.models import AgendaItem, Document


def get_agenda_item(db: Session, number: int):
    return (
        db.query(AgendaItem)
        .filter(number == AgendaItem.number)
        .first()
    )


def create_agenda_item(
        db: Session,
        number: int,
        title: str,
        folder_path: str
):
    agenda = AgendaItem(
        number=number,
        title=title,
        folder_path=folder_path
    )

    db.add(agenda)
    db.commit()
    db.refresh(agenda)

    return agenda


def document_exists(
        db: Session,
        agenda_item_id: int,
        filename: str
):
    return (
            db.query(Document)
            .filter(
                agenda_item_id == Document.agenda_item_id,
                filename == Document.filename
            )
            .first()
            is not None
    )


def create_document(
        db: Session,
        agenda_item_id: int,
        filename: str,
        file_path: str
):
    document = Document(
        agenda_item_id=agenda_item_id,
        filename=filename,
        file_path=file_path
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document
