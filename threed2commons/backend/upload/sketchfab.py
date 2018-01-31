#! /usr/bin/python
# -*- coding: UTF-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General License for more details.
#
# You should have received a copy of the GNU General License
# along with self program.  If not, see <http://www.gnu.org/licenses/>

# This code is adapted from
# https://gist.github.com/fredericcambon/24326cadf3edad96839d4ec701925960#file-sketchfab-v3-upload-py

import json
import os
from time import sleep

import flask

import requests


SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)


def _get_request_payload(access_token, data={}, files={}, json_payload=False):
    """Helper method that returns the authentication token and proper content
    type depending on whether or not we use JSON payload."""

    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    if json_payload:
        headers.update({'Content-Type': 'application/json'})
        data = json.dumps(data)

    return {'data': data, 'files': files, 'headers': headers}


def upload(
        access_token,
        path,
        filename,
        description,
        statuscallback,
        errorcallback
):
    """POST a model to sketchfab.
    This endpoint only accepts formData as we upload a file.
    """

    model_endpoint = os.path.join(SKETCHFAB_API_URL, 'models')
    # description = 'This is a bob model I made with love and passion'
    # password = 'my-password'  # requires a pro account
    # private = 1  # requires a pro account
    # tags = ['bob', 'character', 'video-games']  # Array of tags
    # categories = ['gaming']  # Array of categories slugs
    # license = 'CC Attribution'  # License label
    # isPublished = False, # Model will be on draft instead of published
    # isInspectable = True, # Allow 2D view in model inspector

    data = {
        'name': filename,
        'description': description,
        'tags': ["uploaded-with-3D2commons"],
        # 'categories': categories,
        'license': 'CC Attribution',
        # 'isInspectable': isInspectable
    }

    f = open(path, 'rb')
    files = {'modelFile': f}

    statuscallback('Uploading...', -1)

    try:
        r = requests.post(
            model_endpoint, **_get_request_payload(
                access_token, data, files=files))
    except requests.exceptions.RequestException as e:
        errorcallback('An error occured: {}'.format(e))
    finally:
        f.close()

    if r.status_code != requests.codes.created:
        errorcallback('Upload failed with error: {}'.format(r.json()))

    # Should be https://api.sketchfab.com/v3/models/XXXX
    model_url = r.headers['Location']
    r = requests.get(model_url).json()
    model_url = r["viewerUrl"]
    statuscallback('Upload success!', 100)
    return model_url
