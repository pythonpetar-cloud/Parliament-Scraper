from fastapi import FastAPI, BackgroundTasks, Depends
import uuid
from app.database import engine, get_db
from app.models import Base
from sqlalchemy.orm import Session
from app.tasks import run_scraper
from app.status import create_job, get_job

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Parliament scraper API"
    }


@app.post("/start")
def start_scraper(
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    job_id = str(uuid.uuid4())

    create_job(db, job_id)

    background_tasks.add_task(
        run_scraper,
        job_id
    )

    return {
        "job_id": job_id
    }


@app.get("/status/{job_id}")
def status(
        job_id: str,
        db: Session = Depends(get_db)
):
    return get_job(db, job_id)
