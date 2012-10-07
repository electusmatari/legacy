#!/usr/bin/env python

import wx

from gdulib import rpc
from gdulib import gui
from gdulib import control

appcontrol = control.AppControl()
app = wx.App(False)
frame = gui.MainFrame(appcontrol)
gui.initialize_logging(frame)
appcontrol.initialize(frame)
appcontrol.check_version()
appcontrol.check_token()
app.MainLoop()
