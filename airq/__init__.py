__version__ = '0.1.0'

import json
from api import AP

USERNAME=''
PASSWORD=''

if __name__== "__main__":
  api = API(USERNAME, PASSWORD)
  data = api.get_data()
  print(json.dumps(data.json(), indent=1))
  #api.logout()
