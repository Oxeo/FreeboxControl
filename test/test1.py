#!/usr/bin/python
import sys
import time
sys.path.append('..')
from freeboxctrl import FreeboxCtrl
from freeboxctrl import NetworkError

ctrl = FreeboxCtrl('test.id', 'mafreebox.freebox.fr')

try:
    with open('app_token.txt', 'r') as f:
        appToken = f.read()
except:
    appToken = ''

if appToken == '':
    # Enable application access with the Freebox front panel
    token = ctrl.register('My application name', 'My device', 'v0.1')
    print token
    # Save token
    with open('app_token.txt', 'w') as f:
        appToken = f.write(token)
else:
    ctrl.set_token(appToken)
    #ctrl.play('video', 'http://anon.nasa-global.edgesuite.net/HD_downloads/GRAIL_launch_480.mov')
    while True:
        try:
            status = ctrl.is_freebox_player_on()
            print status;
            time.sleep(1)
        except NetworkError:
            time.sleep(30)


