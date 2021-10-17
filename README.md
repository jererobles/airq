# AirQ

A macOS app that runs on the menu bar and shows air quality from your [uHoo device](https://getuhoo.com/).
<img alt="screenshot" src="airq.png" width="280">

## Run

```bash
$ # clone and install airq
$ git clone git@github.com:jererobles/airq.git && cd airq
$ poetry install

$ # create .env with userId + password
$ cp .env.example .env
$ nano .env

$ # run the venv
$ poetry run python airq/__main__.py
```

AirQ will create a `session` file in the app directory to keep refresh tokens and avoid unnecessary requests to the uHoo API.

## Build

```bash
$ poetry run python setup.py py2app
```

## Statuses

| Emoji | Caused by             | Comments                           |
| ----- | --------------------- | ---------------------------------- |
| ☺️    | –                     | All OK                             |
| 🤢    | Carbon dioxide        | Open the windows                   |
| 🌵    | Low humidity          | Turn on humidifier                 |
| 💦    | High humidity         | Turn on AC                         |
| 😷    | Dust                  | Do some cleaning                   |
| 😣    | Negative air pressure | Open a window                      |
| 😖    | Positive air pressure | Turn off ventilation               |
| 🫁     | Red-brown gases       | Get some fresh air                 |
| 😵    | Various factors       | Air is bad                         |
| ☠️    | Carbon monoxide       | Air is poisonous                   |
| 🦠    | Various factors       | "Virus Index" triggered            |
| ❌    | App error             | Connectivity issues or API changes |

## TODO

-   [x] create initial login script by reversing authentication
-   [x] create class to interface with API
-   [x] use sessions to avoid handling cookies manually
-   [x] persist session after script terminates
-   [x] do something with data
-   [x] make binaries
-   [x] show values in menu bar
