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
from datetime import datetime
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

    scraper = Visma("--headless", "start-maximized")
    scraper.Username = os.getenv("VismaUser")
    scraper.Password = os.getenv("VismaPassword")
    #dump = scraper.scrape()
    url = "https://romsdal-vgs.inschool.visma.no/control/timetablev2/learner/9390648/fetch/ALL/0/current?forWeek=11/04/2024&extra-info=true&types=LESSON,EVENT,ACTIVITY,SUBSTITUTION&_=1712867305697"
    headers = {
        #"Cookie": f"Authorization={dump[0]};XSRF-TOKEN={dump[1]}"
        'Cookie': 'Authorization=eayJ0eXAiOiJKV1QiLCJ0b2tlblR5cGUiOiJBQ0NFU1MiLCJhbGciOiJSUzI1NiJ9.eyJzZXJpYWxpemVkVXNlckRldGFpbHMiOiJINHNJQUFBQUFBQUEvNzFRVVVyRFFCQzlTdG52dGV6T0pwdmRmRm1rYUtGRWlmZ2hVbVJwTm0wdzJaUnNyUlR4T0o3RWl6blRhUEVFRWhieTNzeDdNMi9lMmM3dHR5eG5qTFBYUmNWeWFSS1ZhV001MndkRXFaRDRXL3NDVzFvWHQrNGc3V1UzMU1mMnhVOURqNnFLU2tzWG81L2N1RVB3RVRuUDh2M3c2dEdETEsyeVFpZUdzL1hzZUJxaHRBSE5tUnNoalhiM3MrT3ZwcXAzU0Y2MVpFbG1iWTh3OUJmRkxZS3dSRDFuRzA5azBROXY3b2hzSkp1aDcyTGwyb3ZEaGxSZGlWUjV1NXcvTCtlenNwaVh0RlkzcG9qK2NudGFkZHFFbWpLNHh6VldRSURDbDV5SUgwem1GTEFjelNlSHB2S0QzM3g5K2xENVNYenBXMDh0WGJ6K3U4LzZqdVcxYXlPbTJaelBnM3hONEh5bHJxQVFOczJzVWlKRFluYy9uSFdod2ZNemlaY1Qya0ltQmRVZGhnY3RRVXJBb1EvbjVxYWlrOVVlbDZPMlJSVlovcFJDQXNad2s0akVXdUNDcDZoQ3FiSmdRV3B1cENBV2JKcUM0RGJUSEFuRGxWVUFpb09RS3NtRUdXVUN1MDhlT3VFb0ZmL3pyVENMSDdvbXhxWVBjVXkxK3ZnR2VjSnhKN01DQUFBPSIsImlkIjoiZWQ2OWE4N2UtMzJiNi00NWRkLTg4OTEtZDdmYTgwZTk2MjQ5IiwiaXNNb2JpbGUiOmZhbHNlLCJleHAiOjE3MTI5MDMyNjYsInBhcnRSZWYiOiJkN2NjMzQxNzIxN2RlOTQzZmQ3ODZlMzFmZWMzYjgxNCIsImlzU3VwcG9ydFVzZXIiOmZhbHNlLCJpYXQiOjE3MTI5MDI5NjYsInRlbmFudCI6MTUwMTksInNhbWxDcmVkZW50aWFsc1JlZklkIjoiZGU3NDI1YTctMmE4OC00NjdlLThiNDktNmE1MzJlYmE0ZGUyOjIwMjQtMDQtMTJUMDY6MjI6NDYuNzgzOTkxOTE4IiwidG9rZW5HZW5lcmF0aW9uVmVyc2lvbklkIjoiZjg5ZTgwMzRmMjdlOTI2NDFhZmIxN2RkZTEwN2RhZDQ1Y2FjOTZjNGFlZjc1ZjZhNjdiNzUyNDVmNDgwYWNjZSJ9.kj3zRTWa9Bsn8QsWg2fUO_QTnbaIx72PV9QfQrCc1w-GsV4c1ldPjz-6dBIxk6eealydc6Sojh_s7oXe_aTOxkGyY-Kj7PZtbG4EXPVTao1zLy2D-Eo9ePufRIWVxp5Gwv8zJRTXpZkbQ87tdqOM_j5qnJxKfKBO3KJgp7u2dlfU5p1iCwPYII3RRMZwobI9d-cM7cCIDVe4IPAkU5SbmkQVeH_9ziYLxwqUlSEBjXK1K_pRv4fd6imUVf6BSAqsd6fYnl6l1ap3XiblqMAKhl2cDdA388nJT5qmySmYorsur6y4KsAc4l1ALxNcLU9Jg8OGe-0FYIXF1-IizY-b-Q;XSRF-TOKEN=25d3b46a-4cea-4e58-85c0-5d698b340886'
    }
    r = requests.get(url, headers=headers)
    print(r.status_code)
    print(headers)
    try:
        print(r.json())
    except requests.exceptions.JSONDecodeError:
        dump = scraper.scrape()
        headers = {
        "Cookie": f"Authorization={dump[0]};XSRF-TOKEN={dump[1]}"}
        r = requests.get(url, headers=headers)
    res = r.json()
    for day in res.get("timetableItems"):
        if day.get("date") == datetime.now().strftime("%d/%m/20%y"):
            print(day.get("subject"), day.get("teacherName"))
            print(day)
