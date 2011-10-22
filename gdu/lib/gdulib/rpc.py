import httplib
import json

def rpc_call(auth_token, method, args):
    conn = httplib.HTTPConnection("gradient.electusmatari.com")
    conn.request("POST", "/uploader/json/rpc/",
                 json.dumps({'auth_token': auth_token,
                             'method': method,
                             'args': args}),
                 {'Content-Type': 'text/json'})
    response = conn.getresponse()
    data = response.read()
    if response.status != 200:
        raise RPCError("Bad status from server: %s %s" %
                       (response.status, response.reason))
    try:
        obj = json.loads(data)
    except:
        raise RPCError("Badly formed response: %r" %
                       (data,))
    if 'error' in obj:
        raise RPCError(obj['error'])
    return obj['result']

def check_auth_token(auth_token):
    v = rpc_call(auth_token, 'check_auth_token', None)
    return v['isvalid']

def submit_cache_data(auth_token, data):
    return rpc_call(auth_token, 'submit_cache_data', data)

class RPCError(Exception):
    pass
