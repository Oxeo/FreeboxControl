import httplib
import json
import hmac
from hashlib import sha1
import time
from exceptions import NetworkError
from exceptions import FreeboxError
from exceptions import FreeboxWarning


class FreeboxCtrl:
    def __init__(self, app_id, target='mafreebox.freebox.fr'):
        self.__appId = app_id
        self.__appToken = ''
        self.__sessionToken = ''
        self.__connection = httplib.HTTPConnection(target)

    def register(self, app_name, device_name='FreeboxCtrl', app_version='1.0'):
        body = json.dumps({'app_id': self.__appId, 'app_name': app_name,
                           'app_version': app_version, 'device_name': device_name})
        data = self.__put_json_request('/api/v3/login/authorize/', body)
        if not data['success']:
            raise FreeboxError(data['error_code'] + ': ' + (data['msg']))
        status = 'pending'
        while status == 'pending':
            status = self.__get_app_token_status(data['result']['track_id'])
            time.sleep(1)
        FreeboxCtrl.__check_app_token_status(status)
        self.__appToken = data['result']['app_token']
        return self.__appToken

    def set_token(self, app_token):
        self.__appToken = app_token

    def is_freebox_player_on(self):
        if self.__sessionToken == '':
            self.__start_session()
        data = self.__get_json_request('/api/v3/airmedia/receivers')
        if data['success']:
            for elt in data['result']:
                if elt['name'] == 'Freebox Player':
                    return elt['capabilities']['video']
            return False
        elif data['error_code'] == 'auth_required':
            self.__sessionToken = ''
            raise FreeboxWarning(FreeboxWarning.authRequired)
        else:
            raise FreeboxError(data['error_code'] + ': ' + (data['msg']))

    def play(self, media_type, media):
        if self.__sessionToken == '':
            self.__start_session()
        body = json.dumps({'action': 'start', 'media_type': media_type,
                           'media': media, 'password': ''})
        data = self.__put_json_request('/api/v3/airmedia/receivers/Freebox%20Player/', body)
        return data

    @staticmethod
    def __gen_password(app_token, challenge):
        h = hmac.new(str(app_token), str(challenge), sha1)
        return h.hexdigest()

    def __start_session(self):
        if self.__appToken == '':
            raise FreeboxError(FreeboxError.appTokenUnknown)
        password = FreeboxCtrl.__gen_password(self.__appToken, self.__get_challenge())
        body = json.dumps({'app_id': self.__appId, 'password': password})
        data = self.__put_json_request('/api/v3/login/session/', body)
        if not data['success']:
            raise FreeboxError(data['error_code'] + ': ' + (data['msg']))
        self.__sessionToken = data['result']['session_token']

    def __get_challenge(self):
        data = self.__get_json_request('/api/v3/login/')
        if not data['success']:
            raise FreeboxError(data['error_code'] + ': ' + (data['msg']))
        return data['result']['challenge']

    def __get_app_token_status(self, track_id):
        data = self.__get_json_request('/api/v3/login/authorize/' + str(track_id))
        if not data['success']:
            raise FreeboxError(data['error_code'] + ': ' + (data['msg']))
        return data['result']['status']

    @staticmethod
    def __check_app_token_status(status):
        if status == 'unknown':
            raise FreeboxError(FreeboxError.appTokenUnknown)
        elif status == 'timeout':
            raise FreeboxError(FreeboxError.appTokenTimeout)
        elif status == 'denied':
            raise FreeboxError(FreeboxError.appTokenDenied)

    def __get_json_request(self, url):
        try:
            self.__connection.putrequest("GET", url)
            self.__connection.putheader('Accept', 'text/plain')
            self.__connection.putheader('X-Fbx-App-Auth', self.__sessionToken)
            self.__connection.endheaders()
            response = self.__connection.getresponse()
        except Exception, e:
            self.__connection.close()
            raise NetworkError("Freebox server is not reachable: " + e.message)
        return json.load(response)

    def __put_json_request(self, url, body):
        headers = {'Content-type': 'application/json',
                   'charset': 'utf-8', 'Accept': 'text/plain',
                   'X-Fbx-App-Auth': self.__sessionToken}
        try:
            self.__connection.request('POST', url, body, headers)
            response = self.__connection.getresponse()
        except Exception, e:
            self.__connection.close()
            raise NetworkError("Freebox server is not reachable: " + e.message)
        return json.load(response)