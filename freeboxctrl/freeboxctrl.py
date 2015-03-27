import httplib
import json
import hmac
from hashlib import sha1
import time
import base64
from freeboxexceptions import NetworkError
from freeboxexceptions import FreeboxError
from freeboxexceptions import AppTokenError
import os


class FreeboxCtrl:
    def __init__(self, app_id, target='mafreebox.freebox.fr'):
        self.appToken = ''
        self.__appId = app_id
        self.__sessionToken = ''
        self.__connection = httplib.HTTPConnection(target)

    def register(self, app_name, device_name='FreeboxCtrl', app_version='1.0'):
        body = json.dumps({'app_id': self.__appId, 'app_name': app_name,
                           'app_version': app_version, 'device_name': device_name})
        data = self.__json_request('/api/v3/login/authorize/', body)
        if not data['success']:
            raise FreeboxError(data['error_code'] + ': ' + (data['msg']))
        status = 'pending'
        while status == 'pending':
            status = self.__get_app_token_status(data['result']['track_id'])
            time.sleep(1)
        FreeboxCtrl.__check_app_token_status(status)
        self.appToken = data['result']['app_token']
        return self.appToken
    
    def default_token_location(self):
        return os.path.normpath(os.path.expanduser("~/.FreeboxCtrl_" + self.__appId))
        
    def load_token(self, location=None):
        if location is None:
            location = self.default_token_location()
        with open(location, 'r') as file:
            self.appToken = file.read()
        
    def save_token(self, location=None):
        if location is None:
            location = self.default_token_location()
        with open(location, 'w') as file:
            file.write(self.appToken)

    def remove_token(self, location=None):
        if location is None:
            location = self.default_token_location()
        os.remove(location)
        self.appToken = ''
    
    def set_token(self, token):
        self.appToken = token

    def is_freebox_player_on(self):
        data = self.__authenticated_request('/api/v3/airmedia/receivers')
        for elt in data['result']:
            if elt['name'] == 'Freebox Player':
                return elt['capabilities']['video']
        return False

    def get_files_list(self, folder='/Disque dur/'):
        data = self.__authenticated_request('/api/v3/fs/ls/' + base64.b64encode(folder))
        return data['result']

    def play(self, media_type, media):
        body = json.dumps({'action': 'start', 'media_type': media_type,
                           'media': media, 'password': ''})
        self.__authenticated_request('/api/v3/airmedia/receivers/Freebox%20Player/', body)
        
    def configuration_connection_status(self):
        data = self.__authenticated_request('/api/v3/connection/')
        return data['result']

    def configuration_lan_browser_interfaces(self):
        data = self.__authenticated_request('/api/v3/lan/browser/interfaces/')
        return data['result']

    def configuration_lan_browser(self, interface):
        data = self.__authenticated_request('/api/v3/lan/browser/' + interface + '/')
        return data['result']
    
    def parental_filter_config(self):
        data = self.__authenticated_request('/api/v3/parental/config/')
        return data['result']
    
    def parental_filters(self):
        data = self.__authenticated_request('/api/v3/parental/filter/')
        return data['result']
    
    def parental_filter_get(self, id):
        data = self.__authenticated_request('/api/v3/parental/filter/' + str(id))
        return data['result']
        
    def parental_filter_delete(self, id):
        data = self.__authenticated_request('/api/v3/parental/filter/' + str(id))
        return data['result']

    def __start_session(self):
        self.__sessionToken = ''
        if self.appToken == '':
            raise AppTokenError(AppTokenError.appTokenUnknown)
        password = FreeboxCtrl.__gen_password(self.appToken, self.__get_challenge())
        body = json.dumps({'app_id': self.__appId, 'password': password})
        data = self.__json_request('/api/v3/login/session/', body)
        if not data['success']:
            if data['error_code'] == 'invalid_token':
                raise AppTokenError(AppTokenError.appTokenUnknown)
            raise FreeboxError(data['error_code'] + ': ' + (data['msg']))
        self.__sessionToken = data['result']['session_token']

    def __get_challenge(self):
        data = self.__json_request('/api/v3/login/')
        if not data['success']:
            raise FreeboxError(data['error_code'] + ': ' + (data['msg']))
        return data['result']['challenge']

    def __get_app_token_status(self, track_id):
        data = self.__json_request('/api/v3/login/authorize/' + str(track_id))
        if not data['success']:
            raise FreeboxError(data['error_code'] + ': ' + (data['msg']))
        return data['result']['status']

    def __authenticated_request(self, url, body = None, type = None):
        if self.__sessionToken == '':
            self.__start_session()
        data = self.__json_request(url, body, type)
        if not data['success'] and data['error_code'] == 'auth_required':
            self.__start_session()
            data = self.__json_request(url)
        if not data['success']:
            raise FreeboxError(data['error_code'] + ': ' + (data['msg']))
        return data
    
    def __json_request(self, url, body = None, type = None):
        headers = {'Content-type': 'application/json',
                   'charset': 'utf-8', 'Accept': 'text/plain',
                   'X-Fbx-App-Auth': self.__sessionToken}
        try:
            if type is None:
                if body is None:
                    type = 'GET'
                else:
                    type = "POST"
            self.__connection.request(type, url, body, headers)
            response = self.__connection.getresponse()
        except Exception, e:
            self.__connection.close()
            raise NetworkError("Freebox server is not reachable: " + e.message)
        return json.load(response)

    @staticmethod
    def __gen_password(app_token, challenge):
        h = hmac.new(str(app_token), str(challenge), sha1)
        return h.hexdigest()

    @staticmethod
    def __check_app_token_status(status):
        if status == 'unknown':
            raise AppTokenError(AppTokenError.appTokenUnknown)
        elif status == 'timeout':
            raise AppTokenError(AppTokenError.appTokenTimeout)
        elif status == 'denied':
            raise AppTokenError(AppTokenError.appTokenDenied)