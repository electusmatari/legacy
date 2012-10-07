#!/usr/bin/env python

import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'gradient.settings'
sys.path.append("/home/forcer/Projects/gradient/")

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
