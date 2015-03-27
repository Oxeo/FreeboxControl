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
    myBox.load_token()
except:
    print 'Enable application access with the Freebox front panel'
    myBox.register('My application name', 'My device', 'v0.1')
    myBox.save_token()

# Display files list
try:
    files = myBox.get_files_list('Disque dur/Vidéos')
    for file in files:
        print file['name'] + ' (path = ' + file['path'] + ')'
except AppTokenError:
    myBox.remove_token()
    print "invalid token removed"

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