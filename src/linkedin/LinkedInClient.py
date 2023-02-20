import getpass
import logging
from random import randint
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from user_agent import generate_user_agent
import time
from typing import Any, Dict


default_capabilities = {
    "browserName": "chrome",
    "selenoid:options": {
        "enableVNC": False,
        "enableVideo": False,
        "screenResolution": "640x480",
    },
}


class LinkedInClient:
    def __init__(self, log: Any = logging):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("disable-infobars")
        options.add_argument("start-maximised")
        options.add_argument(f"user-agent={generate_user_agent()}")
        s = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=s, options=options)
        self.log = log

    def __del__(self):
        self.driver.close()

    def enter_password(self, email: str, password: str):
        self.driver.find_element(By.ID, "session_key").click()
        self.driver.find_element(By.ID, "session_key").send_keys(email)
        self.driver.find_element(By.ID, "session_password").click()
        self.driver.find_element(By.ID, "session_password").click()
        self.driver.find_element(By.ID, "session_password").send_keys(password)
        self.driver.find_element(
            By.CSS_SELECTOR, ".sign-in-form__submit-button"
        ).click()

    def enter_pin(self, pin: str):
        self.driver.find_element(By.ID, "input__phone_verification_pin").send_keys(
            pin
        )
        self.driver.find_element(By.ID, "two-step-submit-button").click()

    def goto_main_page(self):
        self.driver.get("https://www.linkedin.com/")
        self.driver.set_window_size(1428, 755)

    def login(self, use_verification_pin=True):
        email = input("Email: ")
        password = getpass.getpass("Password: ")

        self.enter_password(email, password)

        if use_verification_pin:
            pin = input("Pin: ")
            self.enter_pin(pin)

    def simulate_pause(self, start=5, end=8):
        time.sleep(randint(start, end))

    def simulate_press_end(self):
        ActionChains(self.driver).send_keys(Keys.END).perform()

    def try_to_click_more_results(self) -> bool:
        try:
            container = self.driver.find_element(By.CLASS_NAME, "search-results-container")
            button = container.find_element(By.CSS_SELECTOR, ".artdeco-pagination .artdeco-pagination__button--next")
            if button.get_attribute("disabled") == "true":
                return False
            else:
                button.click()
        except:
            return False
        return True

    def get_my_connections(self):
        self.go_to_my_connections()

        total_connections = self.get_total_connections()
        logging.info(f"Total connections: {total_connections}")

        found_connections = self.get_connections()

        while len(found_connections) < total_connections:
            self.simulate_press_end()
            self.simulate_pause(1, 1)

            if not self.try_to_click_more_results():
                break

            self.simulate_pause(1, 3)
            found_connections = found_connections + self.get_connections()

        logging.info(f"Found connections: {len(found_connections)}")

        return found_connections

    def go_to_my_connections(self):
        self.driver.get(
            "https://www.linkedin.com/search/results/people/?network=%5B%22F%22%5D&origin=MEMBER_PROFILE_CANNED_SEARCH&sid=~ea"
        )
        self.simulate_pause(1, 5)

    def get_total_connections(self):
        container = self.driver.find_element(By.CLASS_NAME, "search-results-container")
        text = container.find_element(By.CSS_SELECTOR, "h2").text.strip()
        return int(text.split(" ")[0].replace(",", ""))

    def get_connections(self):
        profiles = []
        try:
            container = self.driver.find_element(By.CLASS_NAME, "search-results-container")
            connections = container.find_elements(By.CLASS_NAME, "entity-result__item")
            for conn in connections:
                container = conn.find_element(By.CLASS_NAME, "entity-result__universal-image")
                anchor = container.find_element(By.CSS_SELECTOR, "a")
                profile_link = anchor.get_attribute("href").split('?')[0]
                profile_id = profile_link.split("/")[-1]

                try:
                    img = container.find_element(By.CSS_SELECTOR, "img")
                    profile_img = img.get_attribute("src")
                except:
                    profile_img = None

                container = conn.find_element(By.CLASS_NAME, "entity-result__content")
                profile_name = container.find_element(By.CLASS_NAME, "entity-result__title-text").find_element(By.CSS_SELECTOR, "a span span").text

                try:
                    profile_occupation = container.find_element(By.CLASS_NAME, "entity-result__primary-subtitle").text
                except:
                    profile_occupation = None

                try:
                    profile_location = container.find_element(By.CLASS_NAME, "entity-result__secondary-subtitle").text
                except:
                    profile_location = None

                try:
                    profile_summary = container.find_element(By.CLASS_NAME, "entity-result__summary").find_element(By.CSS_SELECTOR, "span").text
                    pass
                except:
                    profile_summary = None

                # try:
                #     profile_insight = container.find_element(By.CLASS_NAME, "entity-result__simple-insight-text").find_element(By.CSS_SELECTOR, "strong").text
                #     pass
                # except:
                #     profile_insight = None

                profiles.append(
                    {
                        "profile_id": profile_id,
                        "profile_link": profile_link,
                        "profile_name": profile_name,
                        "profile_img": profile_img,
                        "profile_occupation": profile_occupation,
                        "profile_location": profile_location,
                        "profile_summary": profile_summary,
                    }
                )
        except Exception as e:
            logging.error(f"Getting connections: {e}")
        return profiles

    def get_my_profile(self):
        profile = {}
        try:
            profile_block = self.driver.find_element(By.CLASS_NAME, "feed-identity-module__actor-meta")
            fullname = profile_block.find_element(By.XPATH, "a/div[2]").get_attribute("innerHTML").strip()
            occupation = profile_block.find_element(By.XPATH, "p").get_attribute("innerHTML").strip()

            profile = {
                'fullname': fullname,
                'occupation': occupation,
            }
        except:
            logging.error("Getting profile")

        logging.info(f"Found profile: {str(profile)}")

        return profile


def main(log_level="INFO"):
    logging.basicConfig(
        level=logging.getLevelName(log_level),
        format="%(asctime)s %(levelname)-5s %(name)s (%(module)s-%(lineno)s): %(message)s",
    )

    client = LinkedInClient()
    client.goto_main_page()
    client.login()
    client.simulate_pause(2, 3)
    client.get_my_profile()
    #client.get_my_connections()


if __name__ == "__main__":
    main()
