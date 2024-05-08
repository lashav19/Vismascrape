import os
import urllib
from urllib.parse import unquote, urlparse, parse_qs, urlencode, quote, quote_plus, urljoin
from bs4 import BeautifulSoup
import requests
import re

def parse_url(url: str):
    return url.replace('%252F', '%2F').replace('%253F', '%3F').replace('%253D', '%3D').replace('%2526', '%26').replace('%253A', '%3A').replace('%257C', '%7C').replace('%253A', '%3A')

class visma:
    def __init__(self, url,*, debug=False, hide=True) -> None:
        """
        ? @param debug:  View logs for everything that is happening
        ? @param hide: hides the browser window

        """
        #TODO: implement custom URL
        self.Username = ""
        self.Password = ""
        self.base_url = url if url.endswith('/') else url+"/"
        self.url = self.base_url + "Login.jsp/?idp=feide" 

    def get_auth(self):
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

        req = session.post("https://app.inschool.visma.no/oauth2/code", data=data, allow_redirects=False)
        req = session.get(req.headers.get("Location"), allow_redirects=False)
        parsed_url = urlparse(req.url)
        root_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        req = session.get(root_url, allow_redirects=True, data={Cookie: req.headers.get("Set-Cookie")})

        print("XSRF-TOKEN: ", session.cookies.get_dict().get("XSRF-TOKEN"), "\n")
        print("AUTHORIZATION: ", session.cookies.get_dict().get("Authorization"))

        pattern = r'window\.(\w+)\s*=\s*(.*?);'
        match = re.search(pattern, "window.index_typeId = 9390648;")

        if match:
            learnerID = match.group(2)  # Extract the variable value
            print(f"Variable Value: {learnerID}")


if __name__ == "__main__":
    visma = visma("https://romsdal-vgs.inschool.visma.no")
    visma.Username = os.getenv("VismaUser")
    visma.Password = os.getenv("VismaPassword")
    visma.get_auth() 



