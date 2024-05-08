# python-visma

## Installation

### Install from repo
```
pip install https://github.com/lashav19/python-visma.git
```

### Manually install
```
git clone https://github.com/lashav19/python-visma.git
cd python-visma
python setup.py install
```

Now it is installed in your python packages

## Config

```py
from python_visma import visma

api = visma()
api.Username = "Your username"
api.Password = "Your password"
```

Please use environment variables and / or encrypt your password before putting it in the file to avoid plaintext.

## Usage

```py
data = api.getNextLesson()
```

example return:

```json
{
    "startTime": "09:00",
    "subject": "Math",
    "teacher": "John Doe",
    "endTime": "10:00"
},
```

or if there is no `"next lesson"`:

```json
{
    "startTime": null,
    "subject": null,
    "teacher": null,
    "endTime": null
},
```

## Methods

There are different methods to use in this such as getting the next lesson

```py
# get next lesson
next_lesson = api.getNextLesson()

# get all lessons for today
lessons_today = api.getToday()

# get the whole week
lessons_week = api.getWeek()

# Fetch all json data for the whole week if you want additional data
json_data = api.fetchJsonData()

# get the cookie to send with in an HTTP request
Cookie = api.get_auth()
```

## Customization

This API is set up to have the ability to be used in for example an API or backend server.

Baseline you can use the default methods but if you want to send a request to another endpoint for example you can get the cookie needed in the [header](https://requests.readthedocs.io/en/latest/user/quickstart/#custom-headers).

The `Cookie` variable is already formatted so you can just do:

```py
data = request.get(url, headers=Cookie)

# optionally
data = request.get(url, headers=api.get_auth())
```

## Logging
Custom logging module i made just for debugging, cuz if i use the default logging method i get no info from what i was trying to do.

Incase you want to log with the format of this, this is the function

```py
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
            print(
                f'Vismalib - - [{self.now}]: {Fore.RED + arg + Fore.RESET}')
```
If you have any questions feel free to send me a message on discord `@b4z1c`


## TODO:
[ x ] Add support for "custom" url's (need to test still)

[  ] Integrate new get_auth method into the module 