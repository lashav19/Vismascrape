from urllib.parse import urlparse, parse_qs, quote_plus, urljoin
from bs4 import BeautifulSoup
from datetime import datetime
from colorama import Fore
import warnings
import requests
import urllib
import timeit
import json
import time
import os
import re

# *!?TODO = Bettercomments VSCode extension


class logging: #! Custom logging method to avoid selenium's debug logging
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
            print(
                f'Vismalib - - [{self.now}]: {Fore.RED + arg + Fore.RESET}')


class visma:
    """
    ? A python API to use against Visma In School (VIS) and get lessions and other info
    ? Username: feide username ex: 3 letters of firstname 3 letters of lastname and the date your birthday is (ex: lashav19)
    ? Password: your password that you use on VIS

     ! Please for the love of god DO NOT PUT YOUR PASSWORDS IN PLAINTEXT USE ENVIRONMENT VARIABLES
    """
    
    def __init__(self, url,*, debug=False, hide=True) -> None:
        """
        ? @param debug:  View logs for everything that is happening
        ? @param hide: hides the browser window

        """
        self.Username = ""
        self.Password = ""
        self.base_url = url if url.endswith('/') else url+"/"
        self.url = self.base_url + "Login.jsp/?idp=feide" 


        self.auth = None
        self.learnerid = None

        self.debug = debug
        self.logger = logging(debug=self.debug)
        self.headless = hide

        self.__readAuth()

# "Private" functions

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

    def __filter(self, res, *, filter_type: str = "None") -> dict | list[dict]:
        self.items = []
        self.logger.log(self.items)

        for day in res.get("timetableItems"):
            lesson_time = datetime.strptime(day.get("startTime"), "%H:%M")

            # * Combine date and time and convert datetime
            date_str = day.get("date")
            debug_date = date_str.split('/')
            current_time = datetime.now() if not self.debug else datetime(2024, int(debug_date[1]), int(debug_date[0]), 12, 15)
            day_str, month_str, year_str = date_str.split('/')
            item_date = datetime(int(year_str), int(month_str), int(day_str)).date()
            match filter_type.lower():
                case "next":
                    if lesson_time.time() > current_time.time() and item_date == current_time.date():
                        return{"startTime": day.get("startTime"),
                                "subject": day.get("subject"),
                                "teacher": day.get("teacherName"),
                                "endTime": day.get("endTime")}

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

    def get_auth(self):
        def parse_url(url: str): return url.replace('%252F', '%2F').replace('%253F', '%3F').replace('%253D', '%3D').replace('%2526', '%26').replace('%253A', '%3A').replace('%257C', '%7C').replace('%253A', '%3A')
        session = requests.session()
        response = session.get(self.url, allow_redirects=True)
        parsed_url = urllib.parse.urlparse(response.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        token_input = soup.find('input', {'name': '__RequestVerificationToken'}) #* Find the input field with the name '__RequestVerificationToken'
        request_verification_token = token_input.get("value") #* Get value of requestVerification token
        decoded_url = response.url.replace('%2520', '%20')
        query_params = parse_qs(decoded_url.split('?')[1])
        return_url = query_params.get('ReturnUrl', [''])[0] 

        req = session.post("https://connect.visma.com/external/login", 
                            headers={"Cookie": f'.AspNetCore.Antiforgery.D5MU2Fjo4Ro={session.cookies.get(".AspNetCore.Antiforgery.D5MU2Fjo4Ro")};XSRF-TOKEN={session.cookies.get("XSRF-TOKEN")};.AspNetCore.Culture=c%3Den-US%7Cuic%3Den-US'},
                            allow_redirects=False,
                            data={
                            "AuthenticationScheme": "FeideOIDC",
                            "ProviderName": "Feide",
                            "Action": "Login",
                            "ClientId": "visma-inschool-web-prod",
                            "RememberUsername": "False",
                            "Username": "",
                            "ShouldTriggerSelectAccount": "False",
                            "__RequestVerificationToken": request_verification_token,
                            "ReturnUrl": quote_plus(return_url)
                            })
        req = session.get(req.headers.get("Location"), allow_redirects=False)
        req = session.get(req.headers.get("Location"), allow_redirects=False)
        req = session.get(req.headers.get("Location"), allow_redirects=False)
        req = session.get(req.headers.get("Location"), allow_redirects=False)
        req = session.get(req.headers.get("Location"), allow_redirects=False)
        data = {
            "feidename": os.getenv("VismaUser"),
            "password": os.getenv("VismaPassword")
        }
        req = session.post(req.headers.get("Location"), allow_redirects=True, data=data)
        soup = BeautifulSoup(req.text, 'html.parser')
        SAMLResponse = soup.find('input', {'name': 'SAMLResponse'}).get("value")
        req = session.post("https://auth.dataporten.no/simplesaml/module.php/saml/sp/saml2-acs.php/feide", 
                        data={"SAMLResponse": SAMLResponse})

        soup = BeautifulSoup(req.text, 'html.parser')
        code = soup.find('input', {'name': 'code'}).get("value")
        state = soup.find('input', {'name': 'state'}).get("value")

        Cookie = ";".join(sorted([f"{key}={value}" for key, value in session.cookies.get_dict().items()]))
        Cookie = ";".join([part.strip() for part in Cookie.split(";")])
        postCookie = Cookie.split(";")[2]+";"+Cookie.split(";")[1]+";"+Cookie.split(";")[0]+";"+Cookie.split(";")[6]


        req = session.post(urljoin("https://connect.visma.com", "/signin-feide"), 
                        headers={"Cookie": postCookie,
                                    "Origin": "https://auth.dataporten.no",
                                    "Referer": "https://auth.dataporten.no",
                                    "Sec-Fetch-Site": "cross-site",
                                    },
                        data={"code": code,
                                "state": state}, allow_redirects=False)

        data = {
            ".AspNetCore.Antiforgery.D5MU2Fjo4Ro" : session.cookies.get_dict().get(".AspNetCore.Antiforgery.D5MU2Fjo4Ro"),
            "idsrv.external": session.cookies.get_dict().get("idsrv.external"),
            "idsrv.externalC1": session.cookies.get_dict().get("idsrv.externalC1"),
            "idsrv.externalC2": session.cookies.get_dict().get("idsrv.externalC2"),
            ".AspNetCore.Culture":"c%3Den-US%7Cuic%3Den-US"
        }
        Cookie = "; ".join([f"{key}={value}" for key, value in data.items()])

        req = session.get(urljoin("https://connect.visma.com", parse_url(req.headers.get("Location"))),
                        headers={"Cookie": Cookie}, 
                        allow_redirects=False)

        req = session.get(urljoin("https://connect.visma.com", parse_url(req.headers.get("Location"))),headers={"Cookie": req.headers.get("Set-Cookie")}, )

        soup = BeautifulSoup(req.text, 'html.parser')
        code = soup.find('input', {'name': 'code'}).get("value")
        id_token = soup.find('input', {'name': 'id_token'}).get("value")
        scope = soup.find('input', {'name': 'scope'}).get("value")
        state = soup.find('input', {'name': 'state'}).get("value")
        session_state = soup.find('input', {'name': 'session_state'}).get("value")

        data ={
            "code": code,
            "id_token": id_token,
            "scope": scope,
            "state": state,
            "session_state": session_state
        }
        session.cookies.clear()
        req = session.post("https://app.inschool.visma.no/oauth2/code", data=data, allow_redirects=False)
        req = session.get(req.headers.get("Location"), allow_redirects=False)
        parsed_url = urlparse(req.url)
        root_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        req = session.get(root_url, allow_redirects=True, data={Cookie: req.headers.get("Set-Cookie")})

        pattern = r'window\.(\w+)\s*=\s*(.*?);'
        match = re.search(pattern, "window.index_typeId = 9390648;")

        self.learnerid = match.group(2) if match else None

        self.auth = {"Cookie": f"Authorization={session.cookies.get_dict().get("Authorization")};XSRF-TOKEN={session.cookies.get_dict().get("XSRF-TOKEN")}"}
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
            self.req_url = f'{self.base_url}control/timetablev2/learner/{self.learnerid}/fetch/ALL/0/current?forWeek={datetime.now().date().strftime("%d/%m/20%y")}&extra-info=true&types=LESSON,SUBSTITUTION'
            self.req = requests.get(self.req_url, headers=self.auth)
            self.logger.log(self.req_url)
            if self.req.status_code > 400:
                self.__retry(tries)

            return self.req.json()

        except requests.exceptions.JSONDecodeError:
            self.__retry(tries)

    def getNextLesson(self) -> dict:
        data = self.__filter(self.fetchJsonData(), filter_type="next")
        return data if data else {
            "startTime": None,
            "subject": None,
            "teacher": None,
            "endTime": None
        }

    def getToday(self) -> dict:
        data = self.__filter(self.fetchJsonData(), filter_type="today")
        return data if data else {
            "startTime": None,
            "subject": None,
            "teacher": None,
            "endTime": None
        }

    def getWeek(self):
        return self.__filter(self.fetchJsonData())


if __name__ == "__main__":  # test code

    visma = visma("https://romsdal-vgs.inschool.visma.no", debug=True)
    visma.Username = os.getenv("VismaUser")
    visma.Password = os.getenv("VismaPassword")
    print(visma.getNextLesson())