#!/usr/bin/env python

try:
    import wx

    import api
    import gui
    import control

    app = wx.App(False)
    frame = gui.MainFrame()
    gui.initialize_logging(frame)
    appcontrol = control.AppControl(frame)

    if appcontrol.is_configured_correctly():
        frame.Iconize()

    app.MainLoop()
except:
    import traceback, time
    f = file("C:/Files/log.txt", "a")
    f.write(traceback.format_exc())
    f.close()
    # time.sleep(60)
