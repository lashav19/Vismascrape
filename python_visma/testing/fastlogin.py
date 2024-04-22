
import os
import urllib
from urllib.parse import urlparse, parse_qs, urlencode, quote_plus
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




req3 = session.post("https://connect.visma.com/external/login", 
                    headers=headers,
                    allow_redirects=False,
                    data=params)


print(req3.headers)
#req4 = session.get(req3.url, allow_redirects=False)








# Function to find keys based on the pattern
#print(f"{find_key(session.cookies.get_dict(), pattern=pattern)}={session.cookies.get_dict().get(find_key(session.cookies.get_dict(), pattern=pattern))};")
#print()

#print(".AspNetCore.Antiforgery.D5MU2Fjo4Ro="+session.cookies.get(".AspNetCore.Antiforgery.D5MU2Fjo4Ro")+";")
#print(session.cookies.get_dict())
"""data = {
    req4.url.split("&")[-3].split("=")[0]: req4.url.split("&")[-3].split("=")[1],
    "code": req4.url.split("&")[4].split("=")[1]
}
cookie = ""
for key, value in session.cookies.get_dict().items():
    cookie += f"{key}={value};"""
#print(session.cookies.get_dict())

"""req = session.post("https://connect.visma.com/signin-feide", 
                   headers={"Cookie": cookie, "Referer": "https://auth.dataporten.no/"},
                   data=data,
                   allow_redirects=False)

print(req.status_code)
print(req.headers)
print(req.url)
print(req.text)"""