import os
import re
import cgi

def my_url():
    """
    Return an URL that refers to this script.
    If querystring is True, the query string is appended.
    """
    script_uri = os.getenv("SCRIPT_URI")
    if script_uri is not None:
        return script_uri
    server = os.getenv("HTTP_HOST")
    port = os.getenv("SERVER_PORT", "80")
    script_name = os.getenv("SCRIPT_NAME")
    if path_info is None:
        path_info = os.getenv("PATH_INFO", "")
    query_string = os.getenv("QUERY_STRING", "")
    if server is None or script_name is None:
        raise RuntimeException, "No proper CGI environment"
    if path_info == script_name:
        path_info = ""
    if port == "80":
        port = ""
    else:
        port = ":" + port
    url = "http://" + server + port + script_name + path_info
    if querystring:
        url += "?" + query_string
    return url

def dispatch(l, additionalargs={}):
    path = os.getenv("SCRIPT_URL")
    if path[0] == "/":
        path = path[1:]
    m = None
    for item in l:
        if len(item) == 2:
            (path_re, view) = item
            urlconfargs = {}
        else:
            (path_re, view, urlconfargs) = item
        path_cre = re.compile(path_re)
        m = path_cre.match(path)
        if m:
            kwargs = {}
            kwargs.update(additionalargs)
            kwargs.update(urlconfargs)
            kwargs.update(m.groupdict())
            view_module = __import__("__main__")
            view_f = getattr(view_module, view)
            return view_f(**kwargs)

def redirect(url):
    print("Location: %s" % url)
    print

def tab_menu(l):
    tablist = []
    currtablist = []
    for (url, name) in l:
        tab = Tab(url, name)
        tablist.append(tab)
        currtablist.append(tab)
    currtablist.sort(lambda a, b: cmp(len(b.url), len(a.url)))
    path_info = os.getenv("SCRIPT_URL", "")
    for tab in currtablist:
        if path_info.startswith(tab.url):
            tab.active = True
            break
    html = '<ul class="tabs">'
    for tab in tablist:
        if tab.active:
            cl = ' class="active"'
        else:
            cl = ''
        html += ('<li%s><a href="%s">%s</a></li>' %
                 (cl,
                  cgi.escape(tab.url),
                  cgi.escape(tab.name)))
    html += "</ul>"
    return html

class Tab(object):
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.active = False
