__version__ = '0.1.0'

from Crypto.Cipher import AES
from Crypto import Random
import codecs
import hashlib
import requests

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
  CLIENT_ID = ""

  def __init__(self, username, password):
    self.username = username
    self.password = password
    self.token = None
    self.refreshToken = None
    self.uid = None
    self.clientCode = None

  def _call(self, url="", method="POST", **kwargs):
    return requests.request(method, url, **kwargs)

  def _get_uid(self):
    try:
        response = requests.get(
            url="https://auth.uhooinc.com/user",
            headers={
                "Cookie": "uhoo.sid=s%3As4j2dBbkbg0vXa10iqMHauJBL09TH779.V%2FnuBucub%2B5ylNCnFqXg6CCQwDxbwmXglfuEnvSGVA4",
            },
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
        self.uid = response.json()['uId']
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

  def _get_client_code(self):
    try:
        response = requests.post(
            url="https://auth.uhooinc.com/verifyemail",
            headers={
                "Accept": "*/*",
                "If-None-Match": "W/\"59-lnUAz2k+ZYhT0jjdJV1ylA\"",
                "Accept-Language": "en-FI;q=1.0, fi-FI;q=0.9, de-FI;q=0.8, sv-FI;q=0.7, es-FI;q=0.6, es-419;q=0.5",
                "User-Agent": "uHoo/8.5 (iPhone; XS; iOS 14.2; Scale/3.00)",
                "Host": "auth.uhooinc.com",
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": "uhoo.sid=s%3AD3ZHbTdyXfFPVYMBSf1SEYF170pKVx7y.P5qGKddx95kOSbZbQjmUdvJ0xlHI6YJFypSdCciLETI",
            },
            data={
                "clientId": API.CLIENT_ID,
                "username": self.username,
            },
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
        self.clientCode = response.json()['code']
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

  def login(self):
    self._get_uid()
    self._get_client_code()
    crypto = PasswordCrypto(self.clientCode) # The length of the key here must be a multiple of 16.
    passwordEncrypted = crypto.encrypt(self.uid, self.password).hex()
    try:
        response = requests.post(
            url="https://auth.uhooinc.com/login",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "auth.uhooinc.com",
                "User-Agent": "uHoo/8.5 (iPhone; XS; iOS 14.2; Scale/3.00)",
                "If-None-Match": "W/\"181-g0fFm5C6Eguc5gXFqGxxNQ\"",
                "Accept": "*/*",
                "Accept-Language": "en-FI;q=1.0, fi-FI;q=0.9, de-FI;q=0.8, sv-FI;q=0.7, es-FI;q=0.6, es-419;q=0.5",
                "Cookie": "uhoo.sid=s%3Ap1sv3IZNCIzAS_wNfldiAhvnJM3Lp7xG.hUMP44smYND20i%2FDHhwLXM%2FJjYnxaanAS2n79gYRzgI",
            },
            data={
                "clientId": API.CLIENT_ID,
                "username": self.username,
                "password": passwordEncrypted,
            },
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
        data = response.json()
        self.token = data['token']
        self.refreshToken = data['refreshToken']
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

  def get_data(self):
    try:
        response = requests.get(
            url="https://api.uhooinc.com/v1/getalllatestdata",
            headers={
                "If-None-Match": "W/\"5e4-+882oSbl5AYaIQNdHKHKAw\"",
                "Host": "api.uhooinc.com",
                "Authorization": "Bearer " + self.refreshToken,
                "User-Agent": "uHoo/8.5 (iPhone; XS; iOS 14.2; Scale/3.00)",
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept-Language": "en-FI;q=1.0, fi-FI;q=0.9, de-FI;q=0.8, sv-FI;q=0.7, es-FI;q=0.6, es-419;q=0.5",
                "Cookie": "uhoo.sid=",
            },
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

  def logout(self):
    self._call(API.BASE_URL_API + "")
    pass

if __name__== "__main__":

  api = API('', '')
  api.login()
  api.get_data()
  #api.logout()

  """
  end result password must look like this
  e2edfef01605cc600de7997c55336fc0da04ed13cf6ab2ee2d68be4b6bc2d3f6bb2a5f39
  d3892c92fb76f65a4e1e8f23994aec59310c37b252414f425fce0db6d91adb003df365767d930a6981589e99

  
  e2de06f671b8f820a7433fe6170793457bb20f4b3ad4afd1f77dfdeddf98bfc02c1257df58ef8eb1bcfc4a52

  """