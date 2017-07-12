#!/usr/bin/env python

import datetime
import sys
import os

import nginx.config.builder

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode']
source_suffix = '.rst'
master_doc = 'index'
project = u'Nginx Config Builder'
copyright = u"{year}, LinkedIn".format(year=datetime.datetime.now().year)
pygments_style = 'sphinx'
html_theme = 'default'
