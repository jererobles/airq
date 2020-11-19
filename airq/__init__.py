__version__ = '0.1.0'

from Crypto.Cipher import AES
from Crypto import Random
import codecs
import hashlib
import requests
import pickle
import os
from urllib3.exceptions import InsecureRequestWarning

""" 
  input
    - code: code from email validation endpoint
    - clid: client id -- hardcoded string
    - slt1: some random id I got from a github repo, might break
    - slt2: some hardcoded string I got from the APK source code
    - user: username (email address)
    - pwrd: password
  
  output
    - device status

code = "" # this might need refresh
clid = ""
uid = ""
user = ""
pwrd = ""

"""
class PasswordCrypto:
  SALT = "@uhooinc.com"

  def __init__(self, clientCode):
    self.key = hashlib.md5(clientCode.encode('utf-8')).digest() # initialization key
    self.length = AES.block_size #Initialize the block size
    self.aes = AES.new(self.key, AES.MODE_ECB) #Initialize AES, an instance of ECB mode
      #Truncate function to remove padded characters
    self.unpad = lambda date: date[0:-ord(date[-1])]

  def pad(self, text):
    """
    Fill the function so that the bytecode length of the encrypted data is an integer multiple of block_size
    """
    text = str(text, encoding="utf-8")
    count = len(text)
    add = self.length - (count% self.length)
    entext = text + (chr(add) * add)
    return bytes(entext, encoding='utf-8')

  def encrypt(self, uid, password):
    passwordSalted = uid + password + PasswordCrypto.SALT
    passwordHashed = hashlib.sha256(passwordSalted.encode('utf-8')).hexdigest().encode('utf-8')
    res = self.aes.encrypt(self.pad(passwordHashed))
    return res

  def decrypt(self, decrData):
    res = decrData
    msg = self.aes.decrypt(res).decode("utf8")
    return self.unpad(msg)

class API:
  BASE_URL_AUTH = "https://auth.uhooinc.com/"
  BASE_URL_API = "https://api.uhooinc.com/v1/"
  URL_LOGOUT = BASE_URL_API + "clearusersession"
  URL_GET_DATA = BASE_URL_API + "getalllatestdata"
  URL_LOGIN = BASE_URL_AUTH + "login"
  URL_GET_UID = BASE_URL_AUTH + "user"
  URL_RENEW_TOKEN = BASE_URL_AUTH + "renewusertoken"
  URL_GET_CLIENT_CODE = BASE_URL_AUTH + "verifyemail"
  CLIENT_ID = ""
  SESSION_FILE = "session"

  # these are for storing session info on disk
  UID_HEADER = "X-AIRQ-UID"
  CODE_HEADER = "X-AIRQ-CODE"
  TOKEN_HEADER = "X-AIRQ-TOKEN"

  def __init__(self, username, password, forceLogin=False):
    self.username = username
    self.password = password
    # self.token = None
    # self.refreshToken = None
    self.newSession = True
    self.session = self._get_session(forceLogin)
    if self.newSession: self.login()

  def _get_session(self, forceLogin):
    if os.path.exists(API.SESSION_FILE) and not forceLogin:
      try:
        with open(API.SESSION_FILE, 'rb') as f:
          session = pickle.load(f)
        self.newSession = False
        print('session loaded')
      except:
        print('session loading failed')
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
      print('session created')
    return session

  def _save_session(self):
    with open(API.SESSION_FILE, 'wb') as f:
      pickle.dump(self.session, f)
    print('session saved')

  def _log_response(self, response):
    # shows you queries results: 0 = off, 1 = code, 2 = body, 3 = headers
    log_level = 3
    if log_level > 0:
        label = response.url[response.url.rindex('/')+1:]
        print('[{label}] Response HTTP Status Code: {status_code}'.format(
            label=label, status_code=response.status_code))
    if log_level > 1:
        print('[{label}] Response HTTP Response Body: {content}'.format(
            label=label, content=response.content))
    if log_level > 2:
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
        self.session.headers.update({"Authorization": "Bearer " + response.json()['refreshToken']})
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed: ' + str(e))

  def login(self):
    self._get_uid()
    self._get_client_code()
    crypto = PasswordCrypto(self.session.headers.get(API.CODE_HEADER))
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

  def get_data(self, retry=True):
    try:
        response = self.session.get(url=API.URL_GET_DATA)
        self._log_response(response)
        if response.status_code == 401 and retry == True:
          self._renew_token()
          response = self.get_data(False)
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

if __name__== "__main__":
  requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

  api = API('', '')
  api.get_data()
  #api.logout()
