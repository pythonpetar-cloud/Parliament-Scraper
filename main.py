from scraper import ParliamentScraper
from time import sleep
from random import uniform
from scraper import rename_all, DOWNLOAD_PATH

bot = ParliamentScraper()

bot.login()
sleep(uniform(0.5, 1.5))

try:
    bot.download_docs()
finally:
    bot.logout()
    bot.driver.quit()
    rename_all(DOWNLOAD_PATH)
