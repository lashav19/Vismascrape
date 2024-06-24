from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from colorama import Fore
import requests
import selenium
import json
import time
import os, re


class logging:
    def __init__(self, debug=False, *, time_format="%d/%m/20%y %H:%M:%S"):
        self.debug = debug
        self.format = time_format

    def log(self, *args) -> None:
        self.now = datetime.now().strftime(self.format)
        for arg in args:
            print(f'Vismalib - - [{self.now}]: {arg}') if self.debug else None

    def error(self, *args) -> None:
        self.now = datetime.now().strftime(self.format)
        for arg in args:
            print(f'Vismalib - - [{self.now}]: {Fore.RED + arg + Fore.RESET}')


class visma:
    """
    ? A python API to use against Visma In School (VIS) and get lessions and other info
    ? Username: feide username ex: 3 letters of firstname 3 letters of lastname and the date your birthday is (ex: lashav19)
    ? Password: your password that you use on VIS

     ! Please for the love of god DO NOT PUT YOUR PASSWORDS IN PLAINTEXT USE ENVIRONMENT VARIABLES
    """

    def __init__(self,url, *, debug=False, hide_window=True) -> None:
        """
        ? param debug:  View logs for everything that is happening
        ? param hide: hides the browser window

        """
        self.Username = ""
        self.Password = ""

        self.wait = None
        self.auth = None
        self.learnerid = None

        self.base_url = url if url.endswith('/') else url+"/"
        self.login_url = self.base_url + "Login.jsp/?idp=feide" 

        self.debug = debug
        self.logger = logging(debug=self.debug)
        self.headless = hide_window



        self.__readAuth()

# Private functions

    def __readAuth(self) -> None | bool:
        # * reads the credentials from creds.json
        try:
            with open("creds.json", "r") as file:
                content = file.read()
                self.learnerid = json.loads(content).get("learnerID")
                self.auth = json.loads(content).get("auth")
        except:
            return False

    def __writeAuth(self):
        # * writes the credentials to creds.json
        with open("creds.json", "w") as outfile:
            data = {
                "auth": self.auth,
                "learnerID": self.learnerid
            }
            json.dump(data, outfile)

    def __waitelement(self, byType: By, item: str) -> WebElement:
        # * Waits for an HTML element to avoid crashing
        self.wait = WebDriverWait(self.driver, timeout=10)
        self.wait.until(EC.visibility_of_element_located((byType, item)))

        waited_for = self.driver.find_element(byType, item)
        self.logger.log(f"Waited for {item}")

        return waited_for

    def __filter(self, res, *, filter_type: str = "None") -> dict | list[dict]:
        self.items = []
        self.logger.log(self.items)

        for day in res.get("timetableItems"):
            lesson_time = datetime.strptime(day.get("startTime"), "%H:%M")

            # * Combine date and time and convert datetime
            date_str = day.get("date")
            debug_date = date_str.split('/')
            current_time = datetime.now() if not self.debug else datetime(
                2024, int(debug_date[1]), int(debug_date[0]), 12, 0)
            day_str, month_str, year_str = date_str.split('/')

            item_date = datetime(int(year_str), int(
                month_str), int(day_str)).date()

            match filter_type.lower():
                case "next":
                    return {"startTime": day.get("startTime"),
                            "subject": day.get("subject"),
                            "teacher": day.get("teacherName"),
                            "endTime": day.get("endTime")} if lesson_time.time() > current_time.time() and item_date == current_time.date() else self.items

                case "today":
                    if item_date == current_time.date():
                        self.items.append({
                            "startTime": day.get("startTime"),
                            "subject": day.get("subject"),
                            "teacher": day.get("teacherName"),
                            "endTime": day.get("endTime")
                        })

                case _:
                    self.items.append({
                        "startTime": day.get("startTime"),
                        "subject": day.get("subject"),
                        "teacher": day.get("teacherName"),
                        "endTime": day.get("endTime")
                    })
        return self.items

    def __retry(self, tries=0):
        # * If credentials are invalid it will attempt again
        tries += 1
        if tries == 4:  # max 4 tries
            raise ConnectionAbortedError("Error getting credentials")
        self.logger.error(f"Invalid credentials trying again {tries}")
        self.learnerid = None
        self.auth = None
        self.fetchJsonData(tries=tries)

    # Public

    def get_auth(self) -> tuple[dict, str]:
        """
        #* A method for getting the cookies necessary for use of the in built API
        ? return[0]: is the header for request
        ? return[1]: is the value of learnerID to use towards the api
        """

        self._chrome_driver_path = ChromeDriverManager().install()
        self.service = Service(self._chrome_driver_path)
        self.options = Options()

        if self.headless:
            args = ["--disable-logging", "--headless",
                    "start-maximized", "--log-level=3"]
            for arg in args:
                self.options.add_argument(arg)

        self.logger.log("Started")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.logger.log("Getting URL", )
        self.logger.log(self.login_url)
        self.driver.get(self.login_url)


        username = self.__waitelement(By.ID, "username")
        username.send_keys(self.Username)

        password = self.__waitelement(By.ID, "password")
        password.send_keys(self.Password)

        self.logger.log("Logging in")

        self.driver.find_element(By.CLASS_NAME, "button-primary").click()
        self.auth = {
            "Cookie": f'Authorization={self.driver.get_cookie("Authorization").get("value")};XSRF-TOKEN={self.driver.get_cookie("XSRF-TOKEN").get("value")}'
        }
        match = re.search(r'window\.(\w+)\s*=\s*(.*?);', "window.index_typeId = 9390648;")
        self.learnerid = match.group(2) if match else "Not found"
        self.logger.log("LEARNERID: ",self.learnerid)

        self.__writeAuth()

        return self.auth, self.learnerid

    def fetchJsonData(self, *, tries: int = 0) -> dict:
        """
        *Fetches json data from the visma API
        *if auth is expired it will automatically get credentials

        ?param tries: prevent infinite recursion no use in inputting anything other than 0
        """
        if not self.learnerid or not self.auth:
            self.logger.error("Missing auth, getting auth")
            self.get_auth()

        try:
            self.logger.log(self.auth)
            self.logger.log(self.base_url)
            
            self.url = f'{self.base_url}control/timetablev2/learner/{self.learnerid}/fetch/ALL/0/current?forWeek={datetime.date().strftime("%d/%m/20%y") if not self.debug else "20/05/2024"}&extra-info=true&types=LESSON,SUBSTITUTION'
            
            self.req = requests.get(self.url, headers=self.auth)
            self.logger.log(self.req.status_code)
            
            if self.req.status_code > 400:
                self.__retry(tries)

            return self.req.json()

        except requests.exceptions.JSONDecodeError:
            self.__retry(tries)

    def getNextLesson(self) -> list[dict]:
        data = self.__filter(self.fetchJsonData(), filter_type="next")
        return data if data else {
            "startTime": None,
            "subject": None,
            "teacher": None,
            "endTime": None
        }

    def getToday(self) -> list[dict]:
        data = self.__filter(self.fetchJsonData(), filter_type="today")
        return data if data else {
            "startTime": None,
            "subject": None,
            "teacher": None,
            "endTime": None
        }

    def getWeek(self) -> list[dict]:
        return self.__filter(self.fetchJsonData())


if __name__ == "__main__":  # test code
    startTime = time.perf_counter()
    visma = visma("https://romsdal-vgs.inschool.visma.no/", debug=True)
    visma.Username = os.getenv("VismaUser")
    visma.Password = os.getenv("VismaPassword")
    print("JSONDATA: ", visma.getWeek())
    endTime = time.perf_counter()
    print(f"Elapsed time {endTime-startTime}s", )
