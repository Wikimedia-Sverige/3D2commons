#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (C) 2015-2016, 2018 Zhuyifei1999, Sebastian
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
#

"""threed2commons url extracter."""

import re
from collections import OrderedDict

import pywikibot
import guess_language

SITE = pywikibot.Site()

# File extensions are probably alphanumeric with 0 to 4 chars
RE_EXTENSION = re.compile(r'^[a-z0-9]{0,4}$', re.IGNORECASE)

DEFAULT_LICENSE = '{{subst:nld|<!--replace this template with the license-->}}'
FILEDESC_TEMPLATE = """
=={{int:filedesc}}==
{{Information
|description=%(desc)s
|date=%(date)s
|source=%(source)s
|author=%(uploader)s
|permission=
|other_versions=
|other_fields=
}}

=={{int:license-header}}==
%(license)s
{{LicenseReview}}

[[Category:Uploaded with 3D2commons]]
"""


def make_dummy_desc(filename):
    filedesc = ""
    # filedesc = FILEDESC_TEMPLATE % {
    #     'desc': '',
    #     'date': '',
    #     'source': '',
    #     'uploader': '',
    #     'license': DEFAULT_LICENSE
    # }

    # Remove the extension
    filename = filename.rsplit('.', 1)
    if len(filename) == 1 or RE_EXTENSION.match(filename[1]):
        filename = filename[0]
    else:
        filename = '.'.join(filename)

    return {
        'extractor': '(uploads)',
        'filedesc': filedesc.strip(),
        'filename': sanitize(filename)
    }


def do_extract_url(url):
    """Extract a video url."""
    title = ""

    filedesc = ""
    # filedesc = FILEDESC_TEMPLATE % {
    #     'desc': _desc(title),
    #     'date': "",
    #     'source': url,
    #     'uploader': "",
    #     'license': DEFAULT_LICENSE
    # }

    return {
        'url': url,
        'extractor': title,
        'filedesc': filedesc.strip(),
        'filename': sanitize(title)
    }


def _desc(title):
    desc_orig = desc = title
    desc = escape_wikitext(desc)
    if len(desc_orig) > 100:
        lang = guess_language.guessLanguage(desc_orig)
        if lang != 'UNKNOWN':
            desc = u'{{' + lang + u'|1=' + desc + u'}}'
    return desc


def escape_wikitext(wikitext):
    """Escape wikitext for use in file description."""
    rep = OrderedDict([
        ('{|', '{{(!}}'),
        ('|}', '{{|}}'),
        ('||', '{{!!}}'),
        ('|', '{{!}}'),
        ('[[', '{{!((}}'),
        (']]', '{{))!}'),
        ('{{', '{{((}}'),
        ('}}', '{{))}}'),
        ('{', '{{(}}'),
        ('}', '{{)}}'),
    ])
    rep = dict((re.escape(k), v) for k, v in rep.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], wikitext)


# Source: mediawiki.Title.js@9df363d
sanitationRules = [
    # "signature"
    {
        'pattern': re.compile(ur'~{3}'),
        'replace': ''
    },
    # Space, underscore, tab, NBSP and other unusual spaces
    {
        'pattern': re.compile(ur'[ _\u0009\u00A0\u1680\u180E\u2000-\u200A'
                              ur'\u2028\u2029\u202F\u205F\u3000\s]+'),
        'replace': ' '
    },
    # unicode bidi override characters: Implicit, Embeds, Overrides
    {
        'pattern': re.compile(ur'[\u200E\u200F\u202A-\u202E]'),
        'replace': ''
    },
    # control characters
    {
        'pattern': re.compile(ur'[\x00-\x1f\x7f]'),
        'replace': ''
    },
    # URL encoding (possibly)
    {
        'pattern': re.compile(ur'%([0-9A-Fa-f]{2})'),
        'replace': r'% \1'
    },
    # HTML-character-entities
    {
        'pattern': re.compile(ur'&(([A-Za-z0-9\x80-\xff]+|'
                              ur'#[0-9]+|#x[0-9A-Fa-f]+);)'),
        'replace': r'& \1'
    },
    # slash, colon (not supported by file systems like NTFS/Windows,
    # Mac OS 9 [:], ext4 [/])
    {
        'pattern': re.compile(ur'[:/#]'),
        'replace': '-'
    },
    # brackets, greater than
    {
        'pattern': re.compile(ur'[\]\}>]'),
        'replace': ')'
    },
    # brackets, lower than
    {
        'pattern': re.compile(ur'[\[\{<]'),
        'replace': '('
    },
    # directory structures
    {
        'pattern': re.compile(ur'^(\.|\.\.|\./.*|\.\./.*|.*/\./.*|'
                              ur'.*/\.\./.*|.*/\.|.*/\.\.)$'),
        'replace': ''
    },
    # everything that wasn't covered yet
    {
        'pattern': re.compile(ur'[|#+?:/\\\u0000-\u001f\u007f]'),
        'replace': '-'
    },
]


def sanitize(filename):
    """Sanitize a filename for uploading."""
    for rule in sanitationRules:
        filename = rule['pattern'].sub(rule['replace'], filename)

    return filename


def do_validate_filename(filename):
    """Validate filename for invalid characters/parts."""
    assert len(filename) < 250, 'Your filename is too long'

    for rule in sanitationRules:
        reobj = rule['pattern'].search(filename)
        assert not reobj or reobj.group(0) == ' ', \
            'Your filename contains an illegal part: %r' % reobj.group(0)
    if not filename.endswith(".stl"):
        # Ensure proper file extension.
        filename += ".stl"

    return filename.replace('_', ' ')


def do_validate_filedesc(filedesc):
    """Validate filename for invalid characters/parts."""
    parse = SITE._simple_request(
        action='parse',
        text=filedesc,
        prop='externallinks'
    ).submit()

    externallinks = parse.get('parse', {}).get('externallinks', [])

    if externallinks:
        spam = SITE._simple_request(
            action='spamblacklist',
            url=externallinks
        ).submit()

        assert spam.get('spamblacklist', {}).get('result') != 'blacklisted', \
            ('Your file description matches spam blacklist! Matches: %s' %
             ', '.join(spam.get('spamblacklist', {}).get('matches', [])))

    return filedesc
