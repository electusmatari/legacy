# templates.py --- Tempita connection

# Copyright (C) 2010 Jorgen Schaefer <forcer@forcix.cx>

import os

import tempita

from config import config
from http import HttpResponse

__all__ = ["HttpResponseTemplate", "template_function", "load_template"]

class HttpResponseTemplate(HttpResponse):
    """
    A response object that renders a template.
    """
    def __init__(self, template, templateargs={}, *args, **kwargs):
        t = load_template(template)
        body = t.substitute(templateargs)
        super(HttpResponseTemplate, self).__init__(body, *args, **kwargs)

_template_namespace = {}

def load_template(filename):
    """
    Load an HTML template from a file name.

    See the template_function decorator for how to add functions to
    the namespace.
    """
    full = os.path.join(config.get('templates', 'directory'), filename)
    return tempita.HTMLTemplate.from_filename(full, encoding='utf-8',
                                              get_template=get_file_template,
                                              namespace=_template_namespace)

def get_file_template(name, from_template):
    """
    Fixed tempita.get_file_template to check the parent directory of a
    template.
    """
    path = os.path.join(os.path.dirname(from_template.name),
                        name)
    return from_template.__class__.from_filename(
        path, namespace=from_template.namespace,
        get_template=from_template.get_template)


def template_function(function):
    """
    A decorator to register a template function.
    """
    _template_namespace[function.__name__] = function
    return function
