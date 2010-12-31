#!/usr/bin/env python

import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'emtools.settings'
sys.path.append("/home/forcer/Projects/emtools/")

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
