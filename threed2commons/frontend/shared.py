#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (C) 2015-2016, 2018 Zhuyifei1999, Sebastian Berlin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

"""threed2commons web shared."""

from __future__ import absolute_import

import json
from uuid import uuid4

from flask import session
from redis import Redis

from threed2commons.config import redis_host

redisconnection = Redis(host=redis_host, db=3)


def check_banned():
    """Check for banned cases."""
    return None


def generate_csrf_token():
    """Generate a CSRF token."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = str(uuid4())
    return session['_csrf_token']


def redis_publish(typ, data):
    redisconnection.publish('3d2cnotif:'+typ, json.dumps(data))
