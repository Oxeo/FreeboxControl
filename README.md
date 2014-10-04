FreeboxControl
==============

Control your Freebox with Python (thanks to Freebox API v3.0)


Install
-------
Download and install with:

    $ git clone https://github.com/oxeo/freeboxcontrol
    $ cd freeboxcontrol
    $ sudo python setup.py install


Obtaining an app\_token
-----------------------
This is the first step, the application will ask for an app_token using the following call. A message will be displayed on the Freebox LCD asking the user to grant access to the requesting application.

Once the application has obtained a valid app\_token, it will not have to do this procedure again unless the user revokes the app_token.

```python
from freeboxctrl import FreeboxCtrl

myBox = FreeboxCtrl('test.id')
app_token = myBox.register('My application name')
```

Reference
---------

### Get Freebox Player status (switch on / off)
```python
from freeboxctrl import FreeboxCtrl

myBox = FreeboxCtrl('test.id')
myBox.appToken = app_token

status = myBox.is_freebox_player_on()
```

### Get files list on Freebox disks
```python
files = myBox.get_files_list('Disque dur/Vidéos')
for file in files:
    print file['name'] + ' (path = ' + file['path'] + ')'
```

### Play video on Freebox Player
```python
myBox.play('video', 'http://anon.nasa-global.edgesuite.net/HD_downloads/GRAIL_launch_480.mov')
```
