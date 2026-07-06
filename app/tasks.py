from scraper import ParliamentScraper, rename_all, DOWNLOAD_PATH
from app.status import update_job


def run_scraper(job_id):

    bot = ParliamentScraper()

    try:
        update_job(
            job_id,
            "logging_in",
            "Logging into parliament website"
        )

        bot.login()

        update_job(
            job_id,
            "downloading",
            "Downloading documents"
        )

        bot.download_docs()

        update_job(
            job_id,
            "finished",
            "Download complete"
        )

    except Exception as e:

        update_job(
            job_id,
            "error",
            str(e)
        )

    finally:
        bot.logout()
        bot.driver.quit()
        rename_all(DOWNLOAD_PATH)