#!/usr/bin/env python

import wx

from gdulib import api
from gdulib import gui
from gdulib import control

app = wx.App(False)
frame = gui.MainFrame()
gui.initialize_logging(frame)
appcontrol = control.AppControl(frame)

if appcontrol.is_configured_correctly():
    frame.Iconize()

app.MainLoop()
