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
#

"""threed2commons backend worker."""

from __future__ import absolute_import

import os
import sys
import shutil
import uuid
import urllib

import celery
from celery.contrib.abortable import AbortableTask
from celery.exceptions import Ignore
from redis import Redis
import pywikibot

from threed2commons.exceptions import TaskError, TaskAbort, NeedServerSideUpload
from threed2commons.backend import upload
from threed2commons.backend.upload import sketchfab
from threed2commons.config import (
    redis_pw, redis_host, consumer_key, consumer_secret, http_host,
    uploads_path, pwb_site, ssu_path
)

redisurl = 'redis://:' + redis_pw + '@' + redis_host + ':6379/'
app = celery.Celery(
    'v2cbackend',
    backend=redisurl + '1',
    broker=redisurl + '2'
)
app.conf.CELERY_TASK_RESULT_EXPIRES = 30 * 24 * 3600  # 1 month

app.conf.CELERY_ACCEPT_CONTENT = ['json']

redisconnection = Redis(host=redis_host, db=3, password=redis_pw)


class Stats:
    """Storage for task status."""

    text = ''
    percent = 0


def statuscallback_base(task, stats, text, percent):
    if task.is_aborted():
        raise TaskAbort
    if text is not None:
        stats.text = text
    if percent is not None:
        stats.percent = percent
    print '%d: %s' % (stats.percent, stats.text)

    task.update_state(
        state='PROGRESS',
        meta={'text': stats.text, 'percent': stats.percent}
    )


def errorcallback(text):
    raise TaskError(text)


def prepare_upload(task, url, statuscallback):
    # Get a lock to prevent double-running with same task ID
    lockkey = 'tasklock:' + task.request.id
    if redisconnection.exists(lockkey):
        raise Ignore

    # Check for 10G of disk space, refuse to run if it is unavailable
    st = os.statvfs(ssu_path)
    if st.f_frsize * st.f_bavail < 10 << 30:
        task.retry(max_retries=20, countdown=5*60)
        assert False  # should never reach here

    redisconnection.setex(lockkey, 'T', 7 * 24 * 3600)

    if url.startswith('uploads:'):
        # Local file.
        path = url.replace("uploads:", uploads_path + "/")
    else:
        # Remote file, download needed.
        # TODO: Figure out how to not have to do this multiple times for the
        # same file, when uploading to multiple sources.
        statuscallback('Downloading...', -1)
        filename = url.rsplit("/", 1)[-1]
        directory = os.path.join(uploads_path, str(uuid.uuid1()))
        os.mkdir(directory)
        path = os.path.join(directory, filename)
        print "downloading: {} -> {}".format(url, path)
        try:
            urllib.urlretrieve(url, path)
        except:
            import traceback
            print(traceback.format_exc())
            errorcallback('Download failed!')
    return path


@app.task(bind=True, track_started=False, base=AbortableTask)
def main(
        self, url, ie_key, subtitles, filename, filedesc,
        downloadkey, convertkey, username, oauth
):
    """Main worker code."""

    stats = Stats()

    def statuscallback(text, percent):
        statuscallback_base(self, stats, text, percent)

    path = prepare_upload(self, url, statuscallback)
    try:
        statuscallback('Configuring Pywikibot...', -1)
        pywikibot.config.authenticate[pwb_site] = \
            (consumer_key, consumer_secret) + tuple(oauth)
        pywikibot.Site(user=username).login()

        statuscallback('Uploading...', -1)
        filename, wikifileurl = upload.upload(
            path, filename, url, http_host, filedesc, username,
            statuscallback, errorcallback
        )
        if not wikifileurl:
            errorcallback('Upload failed!')

    except NeedServerSideUpload as e:
        # json serializer cannot properly serialize an exception
        # without losing data, so we change the exception into a dict.
        return {'type': 'ssu', 'hashsum': e.hashsum, 'url': e.url}
    except pywikibot.Error:  # T124922 workaround
        exc_info = sys.exc_info()
        raise TaskError(
            (
                u'pywikibot.Error: %s: %s' % (
                    exc_info[0].__name__, exc_info[1]
                )
            ).encode('utf-8')), None, exc_info[2]
    else:
        statuscallback('Done!', 100)
        return {'type': 'done', 'filename': filename, 'url': wikifileurl}
    finally:
        statuscallback('Cleaning up...', -1)
        pywikibot.stopme()
        pywikibot.config.authenticate.clear()
        pywikibot.config.usernames['commons'].clear()
        pywikibot._sites.clear()


@app.task(bind=True, track_started=False, base=AbortableTask)
def sketchfab_task(self, url, filename, description, access_token):
    stats = Stats()

    def statuscallback(text, percent):
        statuscallback_base(self, stats, text, percent)

    path = prepare_upload(self, url, statuscallback)
    model_url = sketchfab.upload(
        access_token,
        path,
        filename,
        description,
        statuscallback,
        errorcallback
    )
    statuscallback('Done!', 100)
    return {'type': 'done', 'filename': filename, 'url': model_url}
