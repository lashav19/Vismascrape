# Python-visma

## Initialization
```py
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

or if there is no next lesson:
```json
{
    "startTime": null,
    "subject": null,
    "teacher": null,
    "endTime": null
}
```

## Methods
There are different methods to use in this such as getting the next lesson