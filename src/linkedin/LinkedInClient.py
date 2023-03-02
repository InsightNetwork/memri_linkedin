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
import time, pprint, re
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
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("disable-infobars")
        options.add_argument("start-maximised")
        options.add_argument(f"user-agent={generate_user_agent(navigator='chrome')}")
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
        button = self.driver.find_element(By.XPATH, '//form //button[@type="submit"]') # self.test_selector(method='xpath', prompt='submit')
        button.click()

    def is_password_enabled(self):
        try:
            self.driver.find_element(By.ID, "session_password")
            return True
        except:
            return False

    def is_pin_enabled(self):
        try:
            self.driver.find_element(By.ID, "input__phone_verification_pin")
            return True
        except:
            return False

    def enter_pin(self, pin: str):
        self.driver.find_element(By.ID, "input__phone_verification_pin").send_keys(
            pin
        )
        self.driver.find_element(By.ID, "two-step-submit-button").click()
    
    def try_until_success(self, func, **kwargs):
        sleep = kwargs.get('sleep') or 3
        max_tries = kwargs.get('max_tries')
        success = False
        tries = 0
        result = None
        while not success and (not max_tries or tries < max_tries) :
            try:
                result = func(**kwargs)
                success = True if all(result) else False
            except Exception as error:
                logging.warning(f'Error trying function {func} : {error}')
            time.sleep(sleep)
            tries += 1
        return result

    def test_selector(self, method='css', prompt='', container=None, multiple=False):
        """This is for looping and testing various selectors until satisfied
        Usage:
            result = self.test_selector(method='xpath') # try different selectors and methods
        When satisfied:
            result = self.driver.find_element(methods[method], <successful selector>")"""
        success = False
        result = None
        methods = {'xpath': By.XPATH, 'x':  By.XPATH, 'css': By.CSS_SELECTOR, 'c': By.CSS_SELECTOR }
        caller = container or self.driver
        while not success:
            try:
                # print(f'URL {self.driver.current_url}')
                selectr = input(prompt +' selector?')
                if selectr == 'q':
                    success = True
                    return result
                elif selectr.find('method') == 0:
                    method = selectr.rpartition(' ')[-1]
                elif multiple:
                    result = caller.find_elements(methods.get(method), selectr)
                    if result and len(result) > 0:
                        for i, one in enumerate(result):
                            print(f'{i}. {one}, {one.text} , {one.get_attribute("innerHTML").strip()} ')
                            # logging.error(f'result {one}, {one.text} , {one.get_attribute("innerHTML").strip()} ')
                else:
                    result = caller.find_element(methods.get(method), selectr)
                    print(f'result {result}, {result.text} , {result.get_attribute("innerHTML").strip()} ')
                    logging.error(f'result {result}, {result.text} , {result.get_attribute("innerHTML").strip()} ')
            except Exception as error:
                logging.error(f'Error {error}')

    def goto_main_page(self):
        self.driver.get("https://www.linkedin.com/")
        self.driver.set_window_size(700, 1200)

    def goto_profile_page(self):
        self.driver.get("https://www.linkedin.com/in/me")
        self.driver.set_window_size(700, 1200)
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(3)
        
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
    
    def get_my_connections(self, page_callback):
        """page_num is 1-based to correspond to the numbers on LI"""
        page_num = int(input('start page') or 1)
        self.go_to_my_connections(start_page=page_num)
        pages, next_button = self.try_until_success(self.get_all_pagebuttons, max_tries = 3) 
        toppage = int(pages[-1].text) if pages else 1
        logging.warning(f'Total pages {toppage}')
        found_connections = []
       
        while page_num <= toppage: 
            # get connections from current page
            page_connections = self.get_connections()
            logging.warning('page %s connections %s '%(page_num, len(page_connections)))
            page_callback(page_connections)
            found_connections = found_connections + page_connections
            logging.warning(f'Total connections {len(found_connections)} ')
            # now click the next button
            toclick =  next_button
            disabled = toclick.disabled if toclick and hasattr(toclick, 'disabled') else None
            logging.warning('Working on page %s %s disabled %s'%(page_num, next_button, disabled))
            if disabled:
                logging.warning('Disabled, breaking')
                break
            if toclick:
                toclick.click()
                self.simulate_pause(2, 3)
                page_num += 1
                pages, next_button = self.try_until_success(self.get_all_pagebuttons, max_tries = 3) # get again because ellipsis
                if not pages or not next_button:
                    break
                if page_num%5 == 1:
                    y = input(f'Have {len(found_connections)}, page {page_num}. Continue?')
                    if y == 'q':
                        break
            else:
                break

        logging.debug(f"Found connections: {len(found_connections)}")

        return found_connections

    def go_to_my_connections(self, start_page=1):
        self.driver.get(
            f"https://www.linkedin.com/search/results/people/?network=%5B%22F%22%5D&origin=MEMBER_PROFILE_CANNED_SEARCH&page={start_page}"
        )
        self.driver.set_window_size(700, 1200)
        self.simulate_pause(5, 5)

    def get_total_connections(self):
        try:
            container = self.try_to_get(By.CLASS_NAME, "search-results-container")
            text = container.find_element(By.CSS_SELECTOR, "h2").text.strip()
            return int(text.split(" ")[0].replace(",", ""))
        except Exception as e:
            logging.error(f"Getting total connections: {e}")
            return 0

    def get_all_pagebuttons(self, **kwargs):
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(3)
        buttons = self.driver.find_elements(By.CSS_SELECTOR, 'li button') or []
        tester = re.compile("^[0-9]+$")
        pages = [btn for btn in buttons if tester.findall(btn.text.strip())]
        next = self.get_first(By.XPATH, "//button/span[contains(.,'Next')]") 
        pages = pages if len(pages) > 0 else []
        print('found %s pages and next= %s'%(len(pages), type(next)))
        return pages, next

    def get_connections(self):
        profiles = []
        try:
            container = self.try_to_get(By.CLASS_NAME, "search-results-container")
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

    def try_to_get(self, by, path, max_counts=3, min_pause=5, max_pause=10):
        container = None
        counter = 0
        while counter < max_counts and not container:
            try:
                container = self.driver.find_element(by, path)
            except:
                self.simulate_pause(min_pause, max_pause)
            counter = counter + 1

        if not container:
            raise

        return container

    def get_first(self, method, selector, container=None):
        caller = container or self.driver 
        next = caller.find_elements(method, selector) 
        if next and len(next) > 0:
            return next[0]
        return None
    
    def get_all(self, method, selector, container=None):
        caller = container or self.driver 
        results = caller.find_elements(method, selector) 
        return results or []

    def username_from_links(self):
        """gets all linkedin/in links and takes the most common username among them, presumably the user whose profile it is."""
        anchors = self.driver.find_elements(By.XPATH, "//main //a") or []
        logging.warning('Anchors %s'%(len(anchors)))
        urls = [a.get_attribute("href") for a in anchors]
        matcher = re.compile('linkedin.com/in/([a-z0-9\-]*)', re.IGNORECASE)
        them = {}
        for url in urls:
            res = matcher.findall(url)
            if res:
                nm = res[0].lower()
                if nm != 'me':
                    temp = them.setdefault(nm, 0)
                    them[nm] += 1
        std = list(them.items())
        logging.warning('std %s'%(std))
        std.sort(key=lambda x: -x[1])
        username = std[0][0]
        return username

    def get_profile_block(self):
        selector = 'main#main section > div:nth-child(2) > div:nth-child(2)';
        container = self.get_first(By.CSS_SELECTOR, selector)
        # subs = container.find_elements(By.XPATH, '*')
        return container

    def get_about(self):
        try:
            results = self.driver.find_elements(By.XPATH, "//div[@id='about']/ancestor::section")
            if results:
                about_section = results[0]
                spans = self.get_first(By.CSS_SELECTOR, 'div:nth-child(3)', container=about_section)
                return spans.text.strip() 
            else:
                print('No About section')
        except Exception as error:
            logging.warning(f'Error getting About section {error} ')
            return None


    def get_description(self):
        try:
            block = self.get_profile_block()
            # div = self.test_selector(method='xpath', prompt='description', container=block)
            div = block.find_element(By.CSS_SELECTOR, 'div div:nth-child(2)')
            return div.text.strip()
        except Exception as error:
            logging.warning(f'Error getting description {error} ')
            return None

    def get_location(self):
        try:
            block = self.get_profile_block()
            # div = self.test_selector(method='xpath', prompt='location', container=block)
            divs = block.find_elements(By.XPATH, '*')
            loc_block = divs[-1]
            loc = loc_block.find_element(By.XPATH, 'span')
            return loc.text.strip()
        except Exception as error:
            logging.warning(f'Error getting location {error} ')
            return None

    def get_talks_about(self):
        try:
            look_for = 'talks about #'
            block = self.get_profile_block()
            spans = block.find_elements(By.CSS_SELECTOR, 'span')
            for span in spans:
                txt = span.text.lower().strip()
                if txt.find(look_for) == 0:
                    print('talks ', txt.replace(look_for, ''))
                    return txt.replace(look_for, '')
                    break
        except Exception as error:
            logging.warning(f'Error getting "talks about" {error} ')
        return None

    def get_full_profile(self):
        profile = {}
        try:
            handle = self.username_from_links()
            print('handle', handle)
            displayName_cont = self.get_first(By.XPATH, "//main /section //h1")
            displayName = displayName_cont.text.strip() if displayName_cont else 'Unknown name'
            print('fname', displayName)
            description = self.get_description()
            print('desc', description)
            location = self.get_location()
            print('loc', location)
            about = self.get_about()
            talks_about = self.get_talks_about()

            profile = {
                'handle': handle,
                'displayName': displayName,
            }
            if description: profile['description'] = description
            if location: profile['location'] = location
            if about: profile['about'] = about
            if talks_about: profile['talks_about'] = talks_about
        except Exception as e:
            logging.error(f"Getting profile: {e}")

        logging.warning(f"Found profile: {str(profile)}")
        print('returning profile', profile)
        return profile

    def get_my_profile(self):
        profile = {}
        try:
            profile_block = self.try_to_get(By.CLASS_NAME, "feed-identity-module__actor-meta")
            handle = profile_block.find_element(By.XPATH, "a").get_attribute("href").strip('/').split('/')[-1]
            displayName = profile_block.find_element(By.XPATH, "a/div[2]").get_attribute("innerHTML").strip()
            
            profile = {
                'handle': handle,
                'displayName': displayName,
            }
        except Exception as e:
            logging.error(f"Getting profile: {e}")

        if profile and handle:
            try:
                description = profile_block.find_element(By.XPATH, "p").get_attribute("innerHTML").strip()
                if description:
                    profile['desscription'] = description
            except Exception as error:
                logging.warning('No description: %s'%(error))
        logging.warning(f"Found profile: {str(profile)}")

        return profile

    def test_loop(self, test, **kwargs):
        print('testing input', test)
        result = input('please type %s'%test)
        print('true? ', True if result else False)
        return True if result == 'ok' else False


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
