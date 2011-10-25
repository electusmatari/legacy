#!/usr/bin/env python

import wx

from gdulib import rpc
from gdulib import gui
from gdulib import control

app = wx.App(False)
frame = gui.MainFrame()
gui.initialize_logging(frame)
appcontrol = control.AppControl(frame)
appcontrol.check_version()
appcontrol.check_token()
app.MainLoop()
