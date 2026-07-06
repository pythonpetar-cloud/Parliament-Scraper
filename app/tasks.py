from scraper import ParliamentScraper, rename_all, DOWNLOAD_PATH


def run_scraper():
    bot = ParliamentScraper()

    try:
        bot.login()
        bot.download_docs()

    finally:
        bot.logout()
        bot.driver.quit()
        rename_all(DOWNLOAD_PATH)