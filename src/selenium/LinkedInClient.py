
import getpass
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import Any, Dict


default_capabilities = {
    "browserName": "chrome",
    "selenoid:options": {
        "enableVNC": False,
        "enableVideo": False,
        "screenResolution": "640x480",
    }
}


class SeleniumClient:
    def __init__(self, log: Any = logging):
        self.driver = webdriver.Chrome()
        self.log = log

    def __del__(self):
        self.driver.quit()

    def login(self, use_verification_pin=True):
        email = input("Email: ")
        password = getpass.getpass("Password: ")

        self.driver.get("https://www.linkedin.com/")
        self.driver.set_window_size(1428, 755)
        self.driver.find_element(By.ID, "session_key").click()
        self.driver.find_element(By.ID, "session_key").send_keys(email)
        self.driver.find_element(By.ID, "session_password").click()
        self.driver.find_element(By.ID, "session_password").click()
        self.driver.find_element(By.ID, "session_password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, ".sign-in-form__submit-button").click()

        if use_verification_pin:
            pin = input("Pin: ")
            self.driver.find_element(By.ID, "input__phone_verification_pin").send_keys(pin)
            self.driver.find_element(By.ID, "two-step-submit-button").click()

        self.driver.get("https://www.linkedin.com/mynetwork/")



def main(log_level='DEBUG'):
    logging.basicConfig(
        level=logging.getLevelName(log_level),
        format="%(asctime)s %(levelname)-5s %(name)s (%(module)s-%(lineno)s): %(message)s",
    )

    client = SeleniumClient()
    client.login()


if __name__ == '__main__':
    main()
