class NetworkError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FreeboxError(Exception):
    def __init__(self, value):
        self.value = value
        print self.value

    def __str__(self):
        return repr(self.value)


class AppTokenError(Exception):
    appTokenUnknown = 'The app_token is invalid or has been revoked'
    appTokenTimeout = 'The user did not confirmed the authorization within the given time'
    appTokenDenied = 'The user denied the authorization request'

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
