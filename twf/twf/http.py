# http.py --- HTTP abstraction and dispatching

# Copyright (C) 2010 Jorgen Schaefer <forcer@forcix.cx>

import cgi
import re
import urllib
import urlparse
import wsgiref
import wsgiref.headers
import wsgiref.handlers
import wsgiref.util


class URLConf(object):
    """
    A general Django-inspired URL dispatcher.

    >>> u = URLConf([('foo/', foo_view),
                     ('bar/(?P<arg>[0-9]+)/', bar_view, {'arg2': 2})])
    >>> u2 = URLConf([('myapp/', u)])
    >>> u2.dispatch(environ, '/myapp/bar/123/')
    This will call bar_view(environ, arg="123", arg2=2)
    >>> u2.run()
    This will hook this into WSGIRef
    """
    def __init__(self, patterns):
        """
        Create a new URLConf object.

        patterns is a list of tuples or triples. The first element is
        a regular expression, the second a handler, and the third is
        an optional keyword argument dictionary.
        
        If the regular expression matches the path, handler is called.
        If there are named groups in the regular expression, the
        handler is called with those as keyword arguments, in addition
        to the optional keyword arguments from the pattern. If there
        are no named groups, the handler is called with the indexed
        groups as positional arguments, and the optional keyword
        arguments as keyword arguments. In any case, the first
        argument to the handler is the environ from wsgiref.
        """
        self.patterns = []
        for pattern in patterns:
            if len(pattern) == 2:
                (regexp, handler) = pattern
                kwargs = {}
            else:
                (regexp, handler, kwargs) = pattern
            self.patterns.append((re.compile(regexp),
                                  handler,
                                  kwargs))

    def dispatch(self, environ, path):
        """
        Find a handler matching path, and call it with environ.
        """
        for (rx, handler, kwargs) in self.patterns:
            m = rx.match(path)
            if m is not None:
                if hasattr(handler, "dispatch"):
                    return handler.dispatch(environ, path[m.end():])
                d = m.groupdict()
                if len(d) == 0:
                    return handler(environ, *m.groups(), **kwargs)
                else:
                    d.update(kwargs)
                    return handler(environ, **d)
        return None

    def handle(self, environ, start_response, pathinfo="PATH_INFO"):
        """
        Handle a wsgiref call.

        environ is the environ from wsgiref

        start_response is the function to start the response from wsgiref

        pathinfo is an optional keyword where to find the path in
        environ. By default, PATH_INFO is used.
        """
        path = environ[pathinfo]
        path = re.subn("//+", "/", path)
        if path.startswith("/"):
            path = path[1:]
        try:
            response = self.dispatch(environ, path)
        except Exception as e:
            response = HttpTemplateResponse("500.html",
                                            {"error": e},
                                            status="500 Internal Server Error")
        if response is None:
            if environ[pathinfo].endswith("/"):
                response = HttpTemplateResponse("404.html",
                                                {"path": environ[pathinfo]},
                                                status="404 Not Found")
            else:
                url = wsgiref.util.request_uri(environ, False)
                url += "/"
                qs = environ['QUERY_STRING']
                if len(qs) > 0:
                    url += "?" + environ['QUERY_STRING']
                response = HttpResponseRedirect(url)
        start_response(response.status, response.headers.items())
        return response.body

    def run(self, handler=None):
        """
        Run this as a WSGIref application.

        handler is the wsgiref handler to use. By default, the CGI
        handler is used.
        """
        if handler is None:
            handler = wsgiref.handlers.CGIHandler()
        handler.run(self.handle)

class HttpResponse(object):
    """
    A generic HTTP response object.
    """
    def __init__(self, body, content_type="text/html", headers=None,
                 status="200 OK"):
        self.body = body
        if headers is None:
            self.headers = wsgiref.headers.Headers([])
        elif headers.__class__ is wsgiref.headers.Headers:
            self.headers = headers
        else:
            self.headers = wsgiref.headers.Headers(headers)
        self.status = status
        if "Content-Type" not in self.headers:
            self.headers.add_header("Content-Type", content_type)

    def __repr__(self):
        return ("<%s %r, %i headers, %i bytes>" %
                (self.__class__.__name__, self.status, len(self.headers),
                 len(self.body)))

class HttpResponseRedirect(HttpResponse):
    """
    A redirection response.
    """
    def __init__(self, url, body=None, content_type="text/html", headers=None,
                 status="301 Moved Permanently"):
        if body is None:
            t = load_template("301.html")
            body = t.substitute({"destination": url})
        super(HttpResponseRedirect, self).__init__(body, content_type, headers,
                                                   status)
        self.headers.add_header("Location", url)

def adjust_request_uri(environ, path, include_query=True, update_query=False):
    """
    Return a modified address of the current script.

    path is added to the current URL. If it's an absolute path, the
    current path is dropped. If it's relative, it's combined with the
    current path.

    If include_query is False, the query string is dropped.

    If update_query is not False, it's a dictionary with new values
    for certain query string entries. Other query string entries are
    retained. Use a list as the dictionary value to include a query
    string argument more than once.
    """
    url = wsgiref.util.request_uri(environ, False)
    url = urlparse.urljoin(url, path)
    if include_query:
        qs = environ['QUERY_STRING']
        if len(qs) > 0:
            if update_query:
                queries = cgi.parse_qs(qs)
                queries.update(update_query)
                qs = urllib.urlencode(queries, doseq=True)
            url += "?" + qs
    return url
