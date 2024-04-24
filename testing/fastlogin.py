
import os
import urllib
from urllib.parse import unquote, urlparse, parse_qs, urlencode, quote, quote_plus, urljoin
from bs4 import BeautifulSoup
import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    
}

session = requests.session()

response = session.get("https://romsdal-vgs.inschool.visma.no/?idp=feide", allow_redirects=True)
parsed_url = urllib.parse.urlparse(response.url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the input field with the name '__RequestVerificationToken'
token_input = soup.find('input', {'name': '__RequestVerificationToken'})

# Extract the value of the token
if token_input:
    request_verification_token = token_input['value']

params = {
    "AuthenticationScheme": "FeideOIDC",
    "ProviderName": "Feide",
    "Action": "Login",
    "ClientId": "visma-inschool-web-prod",
    "RememberUsername": "False",
    "Username": "",
    "ShouldTriggerSelectAccount": "False",
    "__RequestVerificationToken": request_verification_token
    }
headers = {
    'Host': 'connect.visma.com',
    'Cache-Control': 'max-age=0',
    'Sec-Ch-Ua': '"Chromium";v="123", "Not:A-Brand";v="8"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://connect.visma.com',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Dest': 'document',
    'Referer': response.url,
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Priority': 'u=0, i',
    "Cookie": f'.AspNetCore.Antiforgery.D5MU2Fjo4Ro={session.cookies.get(".AspNetCore.Antiforgery.D5MU2Fjo4Ro")};XSRF-TOKEN={session.cookies.get("XSRF-TOKEN")};.AspNetCore.Culture=c%3Den-US%7Cuic%3Den-US' 
                    
}


# Provided ReturnUrl
provided_url = response.url
decoded_url = provided_url.replace('%2520', '%20')

# Extract the ReturnUrl parameter value
query_params = parse_qs(decoded_url.split('?')[1])
return_url = query_params.get('ReturnUrl', [''])[0]
# Decode the ReturnUrl parameter value
params["ReturnUrl"] = encoded_return_url = quote_plus(return_url)




req = session.post("https://connect.visma.com/external/login", 
                    headers=headers,
                    allow_redirects=False,
                    data=params)


req = session.get(req.headers.get("Location"), allow_redirects=False)
SAML_SESSION = req.headers.get("Set-Cookie")
req = session.get(req.headers.get("Location"), allow_redirects=False)
req = session.get(req.headers.get("Location"), allow_redirects=False)
req = session.get(req.headers.get("Location"), allow_redirects=False)
req = session.get(req.headers.get("Location"), allow_redirects=False)

data = {
    "feidename": os.getenv("VismaUser"),
    "password": os.getenv("VismaPassword")
}


req = session.post(req.headers.get("Location"), allow_redirects=True, data=data)
SAML_AUTHTOKEN = req.headers.get("Set-Cookie")

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

base_url="https://connect.visma.com"




data = {
    ".AspNetCore.Antiforgery.D5MU2Fjo4Ro" : session.cookies.get_dict().get(".AspNetCore.Antiforgery.D5MU2Fjo4Ro"),
    "idsrv.external": session.cookies.get_dict().get("idsrv.external"),
    "idsrv.externalC1": session.cookies.get_dict().get("idsrv.externalC1"),
    "idsrv.externalC2": session.cookies.get_dict().get("idsrv.externalC2"),
    ".AspNetCore.Culture":"c%3Den-US%7Cuic%3Den-US"
}
Cookie = "; ".join([f"{key}={value}" for key, value in data.items()])


headers['Cookie'] = Cookie
headers['Referer'] = "https://auth.dataporten.no/"
headers["Sec-Fetch-Site"] = "cross-site"



encoded_url = req.headers.get("Location").replace('%252F', '%2F').replace('%253F', '%3F').replace('%253D', '%3D').replace('%2526', '%26').replace('%253A', '%3A').replace('%257C', '%7C').replace('%253A', '%3A')


req = session.get(urljoin(base_url, encoded_url),
                  headers={"Cookie": Cookie}, 
                  allow_redirects=False)
encoded_url = req.headers.get("Location").replace('%252F', '%2F').replace('%253F', '%3F').replace('%253D', '%3D').replace('%2526', '%26').replace('%253A', '%3A').replace('%257C', '%7C').replace('%253A', '%3A')




req = session.get(urljoin(base_url, encoded_url),
                  headers={"Cookie": req.headers.get("Set-Cookie")}, )



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
req = session.get(root_url, allow_redirects=True,
                  data={Cookie: req.headers.get("Set-Cookie")})
print(req.url)
print("HEADERS: ",req.headers,"\n")
#print("BODY: ", req.text)





