from sqlalchemy.orm import Session

from app.models import Job


def create_job(db: Session, job_id: str):

    job = Job(
        id=job_id,
        status="created",
        message=""
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def update_job(
    db: Session,
    job_id: str,
    status: str,
    message: str = ""
):

    job = db.get(Job, job_id)

    if job:
        job.status = status
        job.message = message

        db.commit()
        db.refresh(job)

    return job


def get_job(
    db: Session,
    job_id: str
):

    return db.get(Job, job_id)