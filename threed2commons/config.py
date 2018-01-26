#! /usr/bin/python
# -*- coding: UTF-8 -*-
#

"""v2c config loading from json."""

import os as _os
import json as _json

try:
    with open(_os.path.dirname(_os.path.realpath(__file__)) +
              '/../config.json', 'r') as f:
        _data = _json.load(f)
except IOError as _e:
    __import__('logging').exception(_e)
    _data = {}

for key, value in _data.iteritems():
    vars()[key] = value
