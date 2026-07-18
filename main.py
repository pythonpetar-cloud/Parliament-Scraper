from scraper import ParliamentScraper, rename_all, DOWNLOAD_PATH
from time import sleep
from random import uniform

bot = ParliamentScraper()

try:
    bot.login()

    sleep(
        uniform(0.5, 1.5)
    )
    bot.download_docs()

finally:
    bot.logout()
    bot.driver.quit()
    rename_all(DOWNLOAD_PATH)