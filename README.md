# 3D2commons [![Build Status](https://travis-ci.org/Toollabs/video2commons.svg?branch=master)](https://travis-ci.org/Toollabs/video2commons) [![Code Climate](https://codeclimate.com/github/Toollabs/video2commons/badges/gpa.svg)](https://codeclimate.com/github/Toollabs/video2commons) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/470759f4921641c09bda911bbb8569a6)](https://www.codacy.com/app/zhuyifei1999/video2commons?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Toollabs/video2commons&amp;utm_campaign=Badge_Grade)

Transfer 3D files from your hard drive to Commons and other sites. 3D2commons is available for everyone (uses OAuth) via Wikimedia Commons.

Future updates will include (as API:s are made available) uploads from external sites.

## Installing on [Toolforge](https://tools.wmflabs.org/)
1. Copy *config.json.example* to *config.json* and change the default values.
1. Start celery as job:

 `$ cd /path/to/3D2commons`

 `$ jstart celery --workdir=/data/project/threed2commons/3D2commons -A threed2commons.backend.worker worker --loglevel=info --detach`
1. Start webservice:

 `$ webservice --backend=kubernetes python2 start`

## For developers
[Gulp](https://gulpjs.com/) is used to minify html and js files. Be sure to run it when editing the non-minified files.

## See also
* https://tools.wmflabs.org/threed2commons/ - the tool running on Toolforge

## Credits
Developed from [video2commons](https://github.com/toolforge/video2commons).