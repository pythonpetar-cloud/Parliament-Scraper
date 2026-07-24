from scraper import ParliamentScraper, rename_all, DOWNLOAD_PATH
from app.status import update_job
from app.database import SessionLocal


def run_scraper(job_id):
    db = SessionLocal()
    bot = None

    try:
        bot = ParliamentScraper(db)

        update_job(
            db,
            job_id,
            "logging_in",
            "Logging into parliament website"
        )

        bot.login()

        update_job(
            db,
            job_id,
            "downloading",
            "Downloading documents"
        )

        bot.download_docs(db)

        update_job(
            db,
            job_id,
            "finished",
            "Download complete"
        )

    except Exception as e:

        update_job(
            db,
            job_id,
            "error",
            str(e)
        )

    finally:
        if bot:
            bot.logout()
            bot.driver.quit()

        rename_all(DOWNLOAD_PATH)
        db.close()