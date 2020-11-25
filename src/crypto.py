from Crypto.Cipher import AES
from Crypto import Random
import codecs
import hashlib

class Crypto:
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
    passwordSalted = uid + password + Crypto.SALT
    passwordHashed = hashlib.sha256(passwordSalted.encode('utf-8')).hexdigest().encode('utf-8')
    res = self.aes.encrypt(self.pad(passwordHashed))
    return res

  def decrypt(self, decrData):
    res = decrData
    msg = self.aes.decrypt(res).decode("utf8")
    return self.unpad(msg)
