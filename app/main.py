from fastapi import FastAPI, BackgroundTasks
from app.tasks import run_scraper
from app.status import create_job, get_job
import uuid


app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Parliament scraper API"
    }


@app.post("/start")
def start_scraper(background_tasks: BackgroundTasks):

    job_id = str(uuid.uuid4())

    create_job(job_id)

    background_tasks.add_task(
        run_scraper,
        job_id
    )

    return {
        "job_id": job_id
    }


@app.get("/status/{job_id}")
def status(job_id: str):

    return get_job(job_id)