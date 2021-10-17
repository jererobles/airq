import os
import pickle
import requests

STORAGE_FILE = "storage"
USER_AGENT = "uHoo/9.1 (iPhone; XS; iOS 14.4; Scale/3.00)"


class UHooSession(requests.Session):
    """Proxy class to listen for session changes and save to disk

    Does not modify any of the parent's class original behavior. Instead it only watches
    for changes in class attributes that contain information related to the session. If
    one of those attributes changes, the `storage` instance is tasked to save the values.
    """

    def __init__(self, storage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = storage

    def __setattr__(self, k, v):
        old = getattr(self, k, None)
        new = v
        super().__setattr__(k, v)
        # `storage` may have not been defined at this point, since we are overriding the
        # __setattr__ method which the parent class uses to define its own attributes.
        # Defining it before calling super() in the constructor leads to weird behavior.
        if hasattr(self, "storage") and k in ["headers", "cookies"]:
            self.storage.commit(old, new)


class Storage:
    def __init__(self, fpath=STORAGE_FILE):
        self.fpath = fpath
        self.empty = True
        self._sensors = None
        self._session = None
        self._read()

    @property
    def sensors(self):
        # print("[storage] sensors getter read: {s}".format(s=self._sensors))
        return self._sensors

    @property
    def session(self):
        # print("[storage] session getter read: {s}".format(s=self._session))
        if not self._session:
            self._session = self._new_session()
        return self._session

    @sensors.setter
    def sensors(self, value=None):
        if value:
            # print("[storage] sensors setter wrote: {s}".format(s=value))
            self._sensors = value
            self._write()
        return value

    @session.setter
    def session(self, value=None):
        if value:
            # print("[storage] session setter wrote: {s}".format(s=value))
            self._session = value
            self._write()
        return value

    def commit(self, old, new):
        if not old == new:
            self._write()

    def _read(self):
        if os.path.exists(self.fpath):
            try:
                with open(self.fpath, "rb") as f:
                    storage = pickle.load(f)
                    self._sensors = storage["sensors"]
                    self._session = storage["session"]
                # storage reading ok
                # print("[storage] _read: from disk")
            except Exception as e:
                # storage reading error
                logging.exception("[storage] _read: error, from defaults")
                # print(e)
                pass
        else:
            # no storage
            # print("[storage] _read: not found, from defaults")
            pass

    def _write(self):
        with open(self.fpath, "wb") as f:
            storage = {"sensors": self._sensors, "session": self._session}
            pickle.dump(storage, f)

    def _new_session(self):
        session = UHooSession(storage=self)
        session.verify = False
        session.headers = {
            "Accept": "*/*",
            "Host": "auth.uhooinc.com",
            "If-None-Match": 'W/"59-lnUAz2k+ZYhT0jjdJV1ylA"',
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-UK;q=1.0",
            "Accept-Encoding": "gzip;q=1.0, compress;q=0.5",
            "Connection": "close",
        }
        return session
