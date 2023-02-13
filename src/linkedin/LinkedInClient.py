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

    def try_to_click_more_results(self):
        ActionChains(self.driver).send_keys(Keys.HOME).perform()
        time.sleep(0.5)

    def get_my_connections(self):
        self.go_to_my_connections()

        total_connections = self.get_total_connections()
        logging.info(f"Total connections: {total_connections}")

        retries = 0
        prev_connections = []
        found_connections = self.get_connections()

        while len(found_connections) < total_connections:
            self.try_to_click_more_results()
            self.simulate_press_end()
            self.simulate_pause(1, 3)
            prev_connections = found_connections
            found_connections = self.get_connections()

            if len(found_connections) == len(prev_connections):
                retries = retries + 1

                if retries == 3:
                    break
            else:
                retries = 0

        logging.info(f"Found connections: {len(found_connections)}")

        return found_connections

    def go_to_my_connections(self):
        self.driver.get(
            "https://www.linkedin.com/mynetwork/invite-connect/connections/"
        )
        self.simulate_pause(1, 5)

    def get_total_connections(self):
        text = self.driver.find_element(By.CSS_SELECTOR, "header h1").text.strip()
        return int(text.split(" ")[0].replace(",", ""))

    def get_connections(self):
        profiles = []
        try:
            connections = self.driver.find_elements(By.CLASS_NAME, "mn-connection-card")
            for conn in connections:
                anchor = conn.find_element(By.CLASS_NAME, "mn-connection-card__picture")
                profile_link = anchor.get_attribute("href")
                occupation = conn.find_element(
                    By.CLASS_NAME, "mn-connection-card__occupation"
                )
                profile_occupation = occupation.get_attribute("innerHTML").strip()
                name = conn.find_element(By.CLASS_NAME, "mn-connection-card__name")
                profile_name = name.get_attribute("innerHTML").strip()
                profiles.append(
                    {
                        "profile_occupation": profile_occupation,
                        "profile_link": profile_link,
                        "profile_name": profile_name,
                    }
                )
        except:
            logging.error("Getting connections")
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
