import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions
from sqlalchemy.orm import Session
from time import sleep
from random import uniform
import os
import re
from dotenv import load_dotenv
from app.documents import (
    get_agenda_item,
    create_agenda_item,
    document_exists,
    create_document
)

load_dotenv()

CHROME_DRIVER_PATH = os.environ.get('CHROME_DRIVER_PATH')
NAME = os.environ.get('NAME')
PASSWORD = os.environ.get('PASSWORD')

DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "sednica")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)


def human_type(element, text):
    for char in text:
        element.send_keys(char)
        sleep(uniform(0.05, 0.2))


def human_click(driver, element):
    ActionChains(driver).move_to_element(element).pause(uniform(0.3, 0.8)).click().perform()


def clean_filename(name: str) -> str:
    name = name.replace("+", " ")
    name = re.sub(r' +', ' ', name).strip()
    name = re.sub(r'^[A-Z]+\s*-\s*', '', name)
    name = re.sub(r' +', ' ', name).strip()
    name = name[0].upper() + name[1:] if name else name
    return name


def rename_all(path: str):
    """Recursively rename downloaded files inside every item subfolder."""
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename == "title.txt":
                continue  # don't touch our metadata file

            filepath = os.path.join(root, filename)
            base, ext = os.path.splitext(filename)
            new_name = clean_filename(base) + ext
            new_path = os.path.join(root, new_name)

            if filepath != new_path:
                os.rename(filepath, new_path)
                print(f"  {filename} → {new_name}")


def sanitize_filename(name: str, max_bytes: int = 200) -> str:
    """Strip illegal characters and truncate to a safe byte length for the filesystem."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'\s+', " ", name).strip()

    # Truncate by UTF-8 byte length, not character count
    encoded = name.encode("utf-8")
    if len(encoded) > max_bytes:
        encoded = encoded[:max_bytes]
        # avoid cutting in the middle of a multibyte character
        name = encoded.decode("utf-8", errors="ignore")

    return name.strip()


class ParliamentScraper:
    def __init__(self, db=None):
        self.db = db
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("prefs", {
            "download.default_directory": DOWNLOAD_PATH,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
        })

        self.driver = uc.Chrome(options=options, version_main=149)
        self.wait = WebDriverWait(self.driver, 35)
        self.driver.get("https://esednica.novisad.rs/public/#/login")

    def login(self, retries=3):
        for attempt in range(1, retries + 1):
            try:
                username_input = self.driver.find_element(By.ID, "username")
                human_click(self.driver, username_input)
                username_input.clear()
                human_type(username_input, NAME)
                sleep(uniform(0.5, 1.5))

                password_input = self.driver.find_element(By.ID, "password")
                human_click(self.driver, password_input)
                password_input.clear()
                human_type(password_input, PASSWORD)
                sleep(uniform(0.5, 1.5))

                login_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-default[type='submit']")
                human_click(self.driver, login_button)

                session_link = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "a[href='#/sednice']")))
                human_click(self.driver, session_link)

                sleep(uniform(0.5, 1.5))
                rows = self.driver.find_elements(By.CSS_SELECTOR, "tr.item-click")
                human_click(self.driver, rows[1])
                return

            except selenium.common.exceptions.TimeoutException:
                print(f"Attempt {attempt}/{retries} failed — retrying...")
                self.driver.delete_all_cookies()
                self.driver.get("https://esednica.novisad.rs/public/#/login")
                sleep(uniform(1, 3))

        raise Exception("All login attempts failed.")

    def get_item_title(self):
        """Grab the item's title from the 'Назив' row inside the currently open item detail view."""
        title_element = self.wait.until(ec.presence_of_element_located(
            (By.XPATH, "//tr[td[normalize-space(text())='Назив']]/td[2]")
        ))
        return title_element.text.strip()

    def set_download_directory(self, path: str):
        """Redirect Chrome's downloads to a specific folder via CDP."""
        os.makedirs(path, exist_ok=True)
        self.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": path
        })

    def download_docs(self, db: Session, base_dir: str = DOWNLOAD_PATH):
        self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".td-action")))
        total_items = len(self.driver.find_elements(By.CSS_SELECTOR, ".td-action"))
        print(f"Found {total_items} items at the assembly session.")

        main_window = self.driver.current_window_handle
        os.makedirs(base_dir, exist_ok=True)

        for i in range(1, total_items + 1):
            item = self.wait.until(ec.element_to_be_clickable(
                (By.XPATH, f"(//i[contains(@class,'fa-info-circle')])[{i}]")
            ))
            human_click(self.driver, item)

            # Grab the title now that we're inside the item detail view
            title_text = self.get_item_title()
            folder_name = f"{i}. {sanitize_filename(title_text, max_bytes=200 - len(str(i)) - 1)}"
            item_folder = os.path.join(base_dir, folder_name)
            os.makedirs(item_folder, exist_ok=True)
            agenda = get_agenda_item(db, i)
            if agenda is None:
                agenda = create_agenda_item(
                    db,
                    i,
                    title_text
                )

            with open(os.path.join(item_folder, "title.txt"), "w", encoding="utf-8") as f:
                f.write(title_text)

            # Redirect downloads for this item into its own folder
            self.set_download_directory(item_folder)

            panels = ["Документа", "Прилози"]
            for panel_name in panels:
                sleep(uniform(0.5, 1.5))
                try:
                    panel_table = self.driver.find_element(
                        By.XPATH,
                        f"//div[contains(@class,'panel-heading') and contains(normalize-space(text()),"
                        f"'{panel_name}')]/following-sibling::table"
                    )
                except selenium.common.exceptions.NoSuchElementException:
                    print(f"  No table found under '{panel_name}' for item {i}, skipping.")
                    continue

                files = panel_table.find_elements(By.CSS_SELECTOR, ".fa.fa-download")
                total_files = len(files)
                print(f"  Found {total_files} file(s) under '{panel_name}' for item {i} -> {folder_name}")

                for j in range(total_files):
                    panel_table = self.driver.find_element(
                        By.XPATH,
                        f"//div[contains(@class,'panel-heading') and contains(normalize-space(text()),"
                        f"'{panel_name}')]/following-sibling::table"
                    )

                    files = panel_table.find_elements(By.CSS_SELECTOR, ".fa.fa-download")

                    # check files before download
                    before_download = set(os.listdir(item_folder))

                    human_click(self.driver, files[j])

                    sleep(uniform(2, 3))

                    # check files after download
                    after_download = set(os.listdir(item_folder))

                    new_files = after_download - before_download

                    if new_files:
                        old_filename = new_files.pop()
                        old_path = os.path.join(
                            item_folder,
                            old_filename
                        )

                        base, ext = os.path.splitext(old_filename)
                        new_filename = clean_filename(base) + ext
                        new_path = os.path.join(
                            item_folder,
                            new_filename
                        )
                        os.rename(old_path, new_path)
                        print(f"    Renamed: {old_filename} → {new_filename}")

                        if not document_exists(db, agenda.id, new_filename):
                            create_document(
                                db,
                                agenda.id,
                                new_filename,
                                new_path
                            )

                    else:
                        print("    No new file detected")

                    self.driver.switch_to.window(main_window)

            return_button = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, ".fa.fa-reply"))
            )
            self.driver.execute_script("arguments[0].click();", return_button)
            sleep(uniform(0.5, 1.5))

    def logout(self):
        try:
            logout_link = self.wait.until(
                ec.element_to_be_clickable((By.XPATH, "//a[i[contains(@class,'fa-sign-out')]]"))
            )
            human_click(self.driver, logout_link)
            sleep(uniform(1, 2))
            print("Logged out successfully.")
        except Exception as e1:
            print(f"Logout failed (non-fatal): {e1}")
