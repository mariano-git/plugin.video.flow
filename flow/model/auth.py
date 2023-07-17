from typing import List


class Account:
    pass


class LoginModel:
    accounts: List[Account]


class LoginData:
    accountId: str
    password: str
    deviceName: str
    deviceType: str
    devicePlatform: str
    clientCasId: str
    version: str
    type: str
    deviceModel: str
    company: str


class CacheToken:
    pass
