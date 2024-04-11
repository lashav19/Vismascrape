from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from functools import cache
from bs4 import BeautifulSoup
import time
import os
import dotenv
import requests


class Visma:

    Username = ""
    Password = ""

    def __init__(self, *args: str, debug=False) -> None:
        """
        param --headless:  getting json data
        param start-maximized: Initializing the headless
        Put these as empty to see what is going on for testing purposes  
        """
        self.Username = Visma.Username
        self.Password = Visma.Password
        self.chrome_driver_path = ChromeDriverManager().install()
        self.service = Service(self.chrome_driver_path)
        self.options = Options()
        if not debug:
            for arg in args:
                self.options.add_argument(arg)

    # Make the program wait for an element to appear to stop crashing

    def waitUntil(self, byType: By, item: str):

        wait = WebDriverWait(self.driver, timeout=10)
        wait.until(EC.visibility_of_element_located((byType, item)))

        waited_for = self.driver.find_element(byType, item)

        print(f"Waited for {item}")
        return waited_for

    def scrape(self):

        self.driver = webdriver.Chrome(
            service=self.service, options=self.options)

        self.driver.get("https://romsdal-vgs.inschool.visma.no/")

        print("started")  # Debug

        # Visit the desired URL
        self.driver.get("https://romsdal-vgs.inschool.visma.no/")

        # Locate the login button by its name and click it
        time.sleep(.5)

        button = self.waitUntil(By.ID, "onetrust-accept-btn-handler")
        if button:
            button.click()

        login = self.waitUntil(By.ID, "login-with-feide-button")
        login.click()

        print("logging in")

        username = self.driver.find_element(By.ID, "username")
        username.send_keys(self.Username)

        password = self.driver.find_element(By.ID, "password")
        password.send_keys(self.Password)

        self.driver.find_element(By.CLASS_NAME, "button-primary").click()
        print("parsing html")
        return self.driver.get_cookie("Authorization").get("value"), self.driver.get_cookie("XSRF-TOKEN").get("value")


if __name__ == "__main__":

    scraper = Visma("--headless", "start-maximized", debug=True)
    scraper.Username = os.getenv("VismaUser")
    scraper.Password = os.getenv("VismaPassword")
    dump = scraper.scrape()
    url = "https://romsdal-vgs.inschool.visma.no/control/timetablev2/learner/9390648/fetch/ALL/0/current?forWeek=11/04/2024&extra-info=true&types=LESSON,EVENT,ACTIVITY,SUBSTITUTION&_=1712867305697"
    headers = {
        "Cookie": f"Authorization={dump[0]};XSRF-TOKEN={dump[1]}"
    }
    r = requests.get(url, headers=headers)
    res = r.json
    for i in res.get("timetableItems"):
        print(i)
