from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from datetime import time
from colorama import Fore
import os
import requests
import time


class logging:
    def __init__(self,):
        self.format = "%d/%m/20%y %H:%M:%S"

    def log(self, *args) -> None:
        self.now = datetime.now().strftime(self.format)
        for arg in args:
            print(f'Vismalib - - [{self.now}]: "{arg}"', end='\r')

    def error(self, *args) -> None:
        self.now = datetime.now().strftime(self.format)
        for arg in args:
            print(
                f'Vismalib - - [{self.now}]: "{Fore.RED + arg}"' + Fore.RESET)


class vismalib:
    """
    ? A python API to use against Visma In School (VIS) and get lessions and other info
    ? Username: feide username ex: 3 letters of firstname 3 letters of lastname and the date your birthday is (ex: lashav19)
    ? Password: your password that you use on VIS

     ! Please for the love of god DO NOT PUT YOUR PASSWORDS IN PLAINTEXT USE ENVIRONMENT VARIABLES
    """

    Username = ""
    Password = ""

    def __init__(self, debug=False) -> None:
        """
        ? param debug:  View the web browser window as it pops up
        """
        self.Username = vismalib.Username
        self.Password = vismalib.Password
        self.logger = logging()
        self.chrome_driver_path = ChromeDriverManager().install()
        self.service = Service(self.chrome_driver_path)
        self.options = Options()
        self.wait = None
        self.auth = None
        self.learnerid = None
        if not debug:
            args = ["--headless", "start-maximized"]
            for arg in args:
                self.options.add_argument(arg)

    # Waits for an HTML element to avoid crashing
    def waitElement(self, byType: By, item: str):
        self.wait = WebDriverWait(self.driver, timeout=10)
        self.wait.until(EC.visibility_of_element_located((byType, item)))
        waited_for = self.driver.find_element(byType, item)

        self.logger.log(f"Waited for {item}")
        return waited_for

    def __getLearnerID(self, driver):  # "Private" method
        try:
            return driver.execute_script("return currentLearnerId")
        except:
            return False

    def get_auth(self) -> str:
        """
        A method for getting the cookies necessary for use of the in built API
        ? return[0]: is the header for request
        ? return[1]: is the value of learnerID to use towards the api
        """
        self.logger.log("Started")

        self.driver = webdriver.Chrome(
            service=self.service, options=self.options)

        # Open URL
        self.driver.get("https://romsdal-vgs.inschool.visma.no/")
        self.logger.log("Getting URL")

        button = self.waitElement(By.ID, "onetrust-accept-btn-handler")
        if button:
            button.click()

        login = self.waitElement(By.ID, "login-with-feide-button")
        login.click()

        username = self.waitElement(By.ID, "username")
        username.send_keys(self.Username)

        password = self.waitElement(By.ID, "password")
        password.send_keys(self.Password)

        self.logger.log("Logging in")

        self.driver.find_element(By.CLASS_NAME, "button-primary").click()
        self.auth = {
            "Cookie": f'Authorization={self.driver.get_cookie("Authorization").get("value")};XSRF-TOKEN={self.driver.get_cookie("XSRF-TOKEN").get("value")}'
        }
        self.learnerid = self.wait.until(self.__getLearnerID)
        return self.auth, self.learnerid

    def _filter(self, res, *, filter_type: str = "none"):
        self.items = []
        current_time = datetime(2024, 4, 10, 12, 0)
        for day in res.get("timetableItems"):
            time_obj = datetime.strptime(day.get("startTime"), "%H:%M")

            # Combine date and time and convert to Unix timestamp
            date_str = day.get("date")
            day_str, month_str, year_str = date_str.split('/')

            item_date = datetime(int(year_str), int(
                month_str), int(day_str)).date()

            match filter_type.lower():
                case "next":
                    if time_obj.time() > current_time.time() and item_date == current_time.date():
                        return {"startTime": day.get("startTime"),
                                "subject": day.get("subject"), "teacher": day.get("teacherName"),
                                "endTime": day.get("endTime")}
                case "today":
                    if item_date == current_time.date():
                        self.items.append({
                            "startTime": day.get("startTime"),
                            "subject": day.get("subject"),
                            "teacher": day.get("teacherName"),
                            "endTime": day.get("endTime")
                        })

                case "none":
                    self.items.append({
                        "startTime": day.get("startTime"),
                        "subject": day.get("subject"),
                        "teacher": day.get("teacherName"),
                        "endTime": day.get("endTime")
                    })
        return self.items

    def fetchJsonData(self, *, tries=0):
        if not self.learnerid or not self.auth:
            self.logger("Getting auth")
            self.get_auth()

        try:
            self.url = f'https://romsdal-vgs.inschool.visma.no/control/timetablev2/learner/{self.learnerid}/fetch/ALL/0/current?forWeek={datetime.now().date().strftime("%d/%m/20%y")}&extra-info=true&types=LESSON,SUBSTITUTION'
            self.req = requests.get(self.url, headers=self.auth)
            return self.req.json()

        except requests.exceptions.JSONDecodeError:
            tries = 1
            if tries == 4:
                raise ConnectionAbortedError("Error getting credentials")
            self.logger.error("Invalid credentials trying again", tries)
            self.learnerid = None
            self.auth = None
            self.fetchJsonData(tries=tries)

    def getNextLesson(self):
        return self._filter(self.fetchJsonData(), filter_type="next")

    def getToday(self):
        return self._filter(self.fetchJsonData(), filter_type="today")

    def getWeek(self):
        return self._filter(self.fetchJsonData())


if __name__ == "__main__":  # test code

    logger = logging()

    scraper = vismalib()

    #! Please for the love of god DO NOT PUT YOUR PASSWORDS IN PLAINTEXT USE ENVIRONMENT VARIABLES
    scraper.Username = os.getenv("VismaUser")
    scraper.Password = os.getenv("VismaPassword")
    print("Neste time: ", scraper.getNextLesson())
