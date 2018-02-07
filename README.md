# 3D2commons [![Build Status](https://travis-ci.org/Toollabs/video2commons.svg?branch=master)](https://travis-ci.org/Toollabs/video2commons) [![Code Climate](https://codeclimate.com/github/Toollabs/video2commons/badges/gpa.svg)](https://codeclimate.com/github/Toollabs/video2commons) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/470759f4921641c09bda911bbb8569a6)](https://www.codacy.com/app/zhuyifei1999/video2commons?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Toollabs/video2commons&amp;utm_campaign=Badge_Grade)

Transfer 3D files from your harddrive to Commons and other sites. 3D2commons is available for everyone (uses OAuth) via Wikimedia Commons.

Future updates will include (as API:s are made available) uploads from external sites.

## Installing on [Toolforge](https://tools.wmflabs.org/)

1. Download, build and configure [redis](https://redis.io/)-server
 1. Set a password using `requirepass`. This in the same as `redis_pw` in *config.json*.
 1. You may need to change `bind 127.0.0.1` to `bind 0.0.0.0` to be able to connect with flask.
 1. Set `daemonize` to `yes` to run redis-server as daemon.
1. Copy *config.json.example* to *config.json* and change the default values.
1. Start redis-server:

 `$ cd /path/to/redis`

 `$ src/redis-server redis.conf`
1. Start celery:

 `$ cd /path/to/3D2commons`

 `$ celery -A threed2commons.backend.worker worker --loglevel=info --detach --logfile /path/to/logs/celery.log`
1. Start webservice:

 `$ webservice --backend=kubernetes python2 start`

## For developers
[Gulp](https://gulpjs.com/) is used to minify html and js files. Be sure to run it when editing the non-minified files.

## See also
* https://tools.wmflabs.org/threed2commons/
* https://commons.wikimedia.org/wiki/Commons:3D2commons
* https://translatewiki.net/wiki/Translating:3D2commons

## Credits
Developed from [video2commons](https://github.com/toolforge/video2commons).