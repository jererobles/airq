import requests
import pickle
import os
from crypto import Crypto
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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
class API:
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

  # these are for storing session info on disk
  UID_HEADER = "X-AIRQ-UID"
  CODE_HEADER = "X-AIRQ-CODE"
  TOKEN_HEADER = "X-AIRQ-TOKEN"

  def __init__(self, username, password, forceLogin=False):
    self.username = username
    self.password = password
    self.newSession = True
    self.session = self._get_session(forceLogin)
    if self.newSession: self.login()

  def _get_session(self, forceLogin):
    if os.path.exists(API.SESSION_FILE) and not forceLogin:
      try:
        with open(API.SESSION_FILE, 'rb') as f:
          session = pickle.load(f)
        self.newSession = False
      except:
        return self._get_session(True)
    else:
      session = requests.Session()
      session.verify = False
      session.headers = {
        "Accept": "*/*",
        "Host": "auth.uhooinc.com",
        "If-None-Match": "W/\"59-lnUAz2k+ZYhT0jjdJV1ylA\"",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "uHoo/8.5 (iPhone; XS; iOS 14.2; Scale/3.00)",
        "Accept-Language": "en-FI;q=1.0, fi-FI;q=0.9, de-FI;q=0.8, sv-FI;q=0.7, es-FI;q=0.6, es-419;q=0.5",
      }
    return session

  def _save_session(self):
    with open(API.SESSION_FILE, 'wb') as f:
      pickle.dump(self.session, f)

  def _log_response(self, response):
    # shows you queries results: 0 = off, 1 = code, 2 = body, 3 = headers
    log_level = 0
    if log_level > 0:
        label = response.url[response.url.rindex('/')+1:]
        print('[{label}] Response HTTP Status Code: {status_code}'.format(
            label=label, status_code=response.status_code))
    if log_level > 1:
        print('[{label}] Response HTTP Response Body: {content}'.format(
            label=label, content=response.content))
    if log_level > 2:
        print('[{label}] Request HTTP Headers: {content}'.format(
            label=label, content=response.request.headers))
        print('[{label}] Response HTTP Response Headers: {content}'.format(
            label=label, content=response.headers))

  def _get_uid(self):
    try:
        response = self.session.get(url=API.URL_GET_UID)
        self._log_response(response)
        self.session.headers.update({API.UID_HEADER: response.json()['uId']})
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed: ' + str(e))

  def _get_client_code(self):
    try:
        response = self.session.post(
            url=API.URL_GET_CLIENT_CODE,
            data={
                "clientId": API.CLIENT_ID,
                "username": self.username,
            },
        )
        self._log_response(response)
        self.session.headers.update({API.CODE_HEADER: response.json()['code']})
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed: ' + str(e))
  
  def _renew_token(self):
    try:
        response = self.session.post(
            url=API.URL_RENEW_TOKEN,
            data={
                "Token": self.session.headers.get(API.TOKEN_HEADER),
                "userDeviceId": API.CLIENT_ID,
            },
        )
        self._log_response(response)
        if response.status_code == 401:
          self.login()
          return
        data = response.json()
        self.session.headers.update({
          API.TOKEN_HEADER: data['token'],
          "Authorization": "Bearer " + data['refreshToken'],
        })
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed: ' + str(e))

  def login(self):
    self._get_uid()
    self._get_client_code()
    crypto = Crypto(self.session.headers.get(API.CODE_HEADER))
    passwordEncrypted = crypto.encrypt(self.session.headers.get(API.UID_HEADER), self.password).hex()
    try:
        response = self.session.post(
            url=API.URL_LOGIN,
            data={
                "clientId": API.CLIENT_ID,
                "username": self.username,
                "password": passwordEncrypted,
            },
        )
        self._log_response(response)
        data = response.json()
        self.session.headers.update({
          API.TOKEN_HEADER: data['token'],
          "Authorization": "Bearer " + data['refreshToken'],
        })
        self._save_session()
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed: ' + str(e))

  def get_data(self, retry=0):
    try:
        response = self.session.get(url=API.URL_GET_DATA)
        self._log_response(response)
        if (response.status_code == 401 or response.status_code == 403) and retry < 2:
          self._renew_token()
          response = self.get_data(retry+1)
        return response
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed: ' + str(e))

  def logout(self):
    try:
        response = self.session.get(url=API.URL_LOGOUT)
        self.session.headers.pop()
        self._log_response(response)
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed: ' + str(e))