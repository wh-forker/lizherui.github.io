#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'lizherui'
SITENAME = u"lizherui's blog"
SITE_SOURCE = 'https://github.com/lizherui/lizherui.github.io'
SITEURL = 'http://lizherui.github.io'
ARCHIVES_URL = 'archives.html'
GITHUB_URL = 'https://github.com/lizherui'

RELATIVE_URLS = True
DEFAULT_PAGINATION = 5

TIMEZONE = 'Asia/Shanghai'

THEME = 'tuxlite_tbs'

DEFAULT_LANG = u'zh'

DEFAULT_DATE_FORMAT = '%Y-%m-%d'

GOOGLE_ANALYTICS = 'UA-42648273-1'

DISQUS_SITENAME = 'lizherui'

FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_RSS = 'feeds/%s.rss.xml'

# Blogroll
LINKS =  (('Python.org', 'http://python.org/'),
          ('Pelican', 'http://getpelican.com/'),
          ('Jinja2', 'http://jinja.pocoo.org/'),
         )

# Social widget
SOCIAL = (('rss', 'http://lizherui.github.io/feeds/all.rss.xml'),
          ('github', 'https://github.com/lizherui'),
          ('weibo', 'http://weibo.com/lzrm4a1'),
          ('zhihu', 'http://www.zhihu.com/people/li-zhe-rui'),
          ('twitter', 'https://twitter.com/lzrak47'),
        )

