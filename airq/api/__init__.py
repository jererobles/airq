"""
  input
    - code: code from email validation endpoint
    - clid: client id -- hardcoded string
    - slt1: uid you get from preauth step
    - slt2: some hardcoded string I got from the APK source code
    - user: username (email address)
    - pwrd: password

  output
    - device status
"""

import os
import pickle
import requests
from urllib3.exceptions import InsecureRequestWarning
from airq.api.crypto import Crypto

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class Uhoo:
    BASE_URL_AUTH = "https://auth.uhooinc.com/"
    BASE_URL_API = "https://api.uhooinc.com/v1/"
    URL_LOGOUT = BASE_URL_API + "clearusersession"
    URL_GET_DATA = BASE_URL_API + "getalllatestdata"
    URL_LOGIN = BASE_URL_AUTH + "login"
    URL_GET_UID = BASE_URL_AUTH + "user"
    URL_RENEW_TOKEN = BASE_URL_AUTH + "renewusertoken"
    URL_GET_CLIENT_CODE = BASE_URL_AUTH + "verifyemail"
    CLIENT_ID = "85E7D9B2-4876-4E2C-BFB5-87FB4918A0E42"
    SESSION_FILE = "session"
    USER_AGENT = "uHoo/9.1 (iPhone; XS; iOS 14.4; Scale/3.00)"

    # these are for storing session info on disk
    UID_HEADER = "X-AIRQ-UID"
    CODE_HEADER = "X-AIRQ-CODE"
    TOKEN_HEADER = "X-AIRQ-TOKEN"

    def __init__(self, username, password, renew_login=False):
        self.username = username
        self.password = password
        self.new_session = True
        self.session = self._get_session(renew_login)
        if self.new_session:
            self.login()

    def _get_session(self, renew_login):
        if os.path.exists(Uhoo.SESSION_FILE) and not renew_login:
            try:
                with open(Uhoo.SESSION_FILE, "rb") as f:
                    session = pickle.load(f)
                self.new_session = False
            except:
                return self._get_session(True)
        else:
            session = requests.Session()
            session.verify = False
            session.headers = {
                "Accept": "*/*",
                "Host": "auth.uhooinc.com",
                "If-None-Match": 'W/"59-lnUAz2k+ZYhT0jjdJV1ylA"',
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": Uhoo.USER_AGENT,
                "Accept-Language": "en-UK;q=1.0",
                "Accept-Encoding": "gzip;q=1.0, compress;q=0.5",
                "Connection": "close",
            }
        return session

    def _save_session(self):
        with open(Uhoo.SESSION_FILE, "wb") as f:
            pickle.dump(self.session, f)

    def _log_response(self, response):
        # shows you queries results: 0 = off, 1 = code, 2 = body, 3 = headers
        log_level = 3
        if log_level > 0:
            label = response.url[response.url.rindex("/") + 1 :]
            print(
                "[{label}] Response HTTP Status Code: {status_code}".format(
                    label=label, status_code=response.status_code
                ),
                flush=True,
            )
        if log_level > 1:
            print(
                "[{label}] Response HTTP Response Body: {content}".format(
                    label=label, content=response.content
                ),
                flush=True,
            )
        if log_level > 2:
            print(
                "[{label}] Request HTTP Headers: {content}".format(
                    label=label, content=response.request.headers
                ),
                flush=True,
            )
            print(
                "[{label}] Response HTTP Response Headers: {content}".format(
                    label=label, content=response.headers
                ),
                flush=True,
            )

    def _get_uid(self):
        try:
            response = self.session.get(url=Uhoo.URL_GET_UID)
            self._log_response(response)
            self.session.headers.update({Uhoo.UID_HEADER: response.json()["uId"]})
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed: " + str(e))

    def _get_client_code(self):
        try:
            response = self.session.post(
                url=Uhoo.URL_GET_CLIENT_CODE,
                data={
                    "clientId": Uhoo.CLIENT_ID,
                    "username": self.username,
                },
            )
            self._log_response(response)
            self.session.headers.update({Uhoo.CODE_HEADER: response.json()["code"]})
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed: " + str(e))

    def _renew_token(self):
        try:
            response = self.session.post(
                url=Uhoo.URL_RENEW_TOKEN,
                data={
                    "Token": self.session.headers.get(Uhoo.TOKEN_HEADER),
                    "userDeviceId": Uhoo.CLIENT_ID,
                },
            )
            self._log_response(response)
            if response.status_code == 401:
                self.login()
                return
            data = response.json()
            self.session.headers.update(
                {
                    Uhoo.TOKEN_HEADER: data["token"],
                    "Authorization": "Bearer " + data["refreshToken"],
                }
            )
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed: " + str(e))

    def login(self):
        self._get_uid()
        self._get_client_code()
        crypto = Crypto(self.session.headers.get(Uhoo.CODE_HEADER))
        pass_encrypted = crypto.encrypt(
            self.session.headers.get(Uhoo.UID_HEADER), self.password
        ).hex()
        try:
            response = self.session.post(
                url=Uhoo.URL_LOGIN,
                data={
                    "clientId": Uhoo.CLIENT_ID,
                    "username": self.username,
                    "password": pass_encrypted,
                },
            )
            self._log_response(response)
            data = response.json()
            self.session.headers.update(
                {
                    Uhoo.TOKEN_HEADER: data["token"],
                    "Authorization": "Bearer " + data["refreshToken"],
                }
            )
            self._save_session()
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed: " + str(e))

    def get_data(self, retry=0):
        try:
            response = self.session.get(url=Uhoo.URL_GET_DATA)
            self._log_response(response)
            if (
                response.status_code == 401 or response.status_code == 403
            ) and retry < 2:
                self._renew_token()
                response = self.get_data(retry + 1)
            return response
        except requests.exceptions.RequestException as e:
            message = "HTTP Request failed: " + str(e)
            print(message)
            return message

    def logout(self):
        try:
            response = self.session.get(url=Uhoo.URL_LOGOUT)
            self.session.headers.pop()
            self._log_response(response)
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed: " + str(e))
