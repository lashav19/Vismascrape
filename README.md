# python-visma

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

If you have any questions feel free to send me a message on discord `@b4z1c`
