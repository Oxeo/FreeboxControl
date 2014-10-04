#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
sys.path.append('..')
from freeboxctrl import FreeboxCtrl
from freeboxctrl import NetworkError
from freeboxctrl import AppTokenError

myBox = FreeboxCtrl('test.id', 'mafreebox.freebox.fr')

try:
    with open('app_token.txt', 'r') as f:
        appToken = f.read()
except:
    appToken = ''

if appToken == '':
    print 'Enable application access with the Freebox front panel'
    token = myBox.register('My application name', 'My device', 'v0.1')
    # Save token
    with open('app_token.txt', 'w') as f:
        f.write(token)
else:
    myBox.appToken = appToken

# Display files list
files = myBox.get_files_list('Disque dur/Vidéos')
for file in files:
    print file['name'] + ' (path = ' + file['path'] + ')'

# Play video
#ctrl.play('video', 'http://anon.nasa-global.edgesuite.net/HD_downloads/GRAIL_launch_480.mov')

# Check Freebox Player status (on / off)
while True:
    try:
        status = myBox.is_freebox_player_on()
        print status
        time.sleep(1)
    except NetworkError:
        time.sleep(30)
    except AppTokenError, e:
        print e
        with open('app_token.txt', 'w') as f:
            f.write('')
        exit(0)