#!/usr/bin/env python

import wx

from gdulib import rpc
from gdulib import gui
from gdulib import control

app = wx.App(False)
frame = gui.MainFrame()
gui.initialize_logging(frame)
appcontrol = control.AppControl(frame)
if not appcontrol.auth_token_ok:
    if appcontrol.auth_token == "":
        message = ("You have not configured an authentication token yet. "
                   "You will not be able to upload data until you have done "
                   "so.")
    else:
        message = ("The authentication token you have specified is invaid. "
                   "Please configure a correct token.")
    appcontrol.configuration_problem(message)
app.MainLoop()
