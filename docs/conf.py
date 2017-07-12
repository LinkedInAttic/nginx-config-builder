#!/usr/bin/env python

import datetime
import sys
import os

sys.path.insert(0, '../src')

import nginx.config.builder
import nginx.config.api
import nginx.config.common
import nginx.config.helpers

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode']
source_suffix = '.rst'
master_doc = 'index'
project = u'Nginx Config Builder'
copyright = u"{year}, LinkedIn".format(year=datetime.datetime.now().year)
pygments_style = 'sphinx'
html_theme = 'default'
