# -*- coding: UTF-8 -*-
#
# Copyright (C) 2018 Sebastian Berlin
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>`

import requests
import flask

from threed2commons import config

def oauth_init():
    authorize_url = "https://sketchfab.com/oauth2/authorize/"
    url = '{}?response_type=code&client_id={}&redirect_uri={}'.format(
        authorize_url,
        config.sketchfab_client_id,
        config.sketchfab_redirect_uri
    )

    return url


def oauth_redirect(code):
    access_token_url = "https://sketchfab.com/oauth2/token/"
    response = requests.post(
        access_token_url,
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': config.sketchfab_client_id,
            'client_secret': config.sketchfab_client_secret,
            'redirect_uri': config.sketchfab_redirect_uri
        }
    )
    access_token = response.json()["access_token"]
    flask.session["sketchfab_access_token"] = access_token
