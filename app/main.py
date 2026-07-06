from fastapi import FastAPI, BackgroundTasks
from app.tasks import run_scraper

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Parliament scraper API"}


@app.post("/start")
def start_scraper(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_scraper)

    return {
        "status": "started"
    }