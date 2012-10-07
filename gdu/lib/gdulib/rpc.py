import httplib
import json
import traceback

def rpc_call(method, args):
    try:
        conn = httplib.HTTPConnection("gradient.electusmatari.com")
        conn.request("POST", "/uploader/json/rpc/%s/" % method,
                     json.dumps(args),
                     {'Content-Type': 'text/json'})
        response = conn.getresponse()
        data = response.read()
    except Exception as e:
        raise RPCError("Error %s from RPC server: %s" %
                       (e.__class__.__name__, str(e)))
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
    return rpc_call('check', {'auth_token': auth_token})

def submit_cache_data(auth_token, data):
    data = data.copy()
    data['auth_token'] = auth_token
    return rpc_call('submit', data)

def submit_exception(auth_token, text):
    return rpc_call('exception',
                    {'auth_token': auth_token,
                     'description': text,
                     'trace': traceback.format_exc()})

class RPCError(Exception):
    pass
