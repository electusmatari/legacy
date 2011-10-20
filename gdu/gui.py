#!/usr/bin/env python

import logging
import sys

import wx

import api
import handler
import version

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None,
                          title='Gradient Data Uploader',
                          size=(600, 480))
        self.statusbar = self.CreateStatusBar()

        panel = wx.Panel(self)
        self.notebook = Notebook(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)

        icon = wx.Icon('grd.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.trayicon = None

        self.Bind(wx.EVT_ICONIZE, self.on_iconify)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.Layout()
        self.Show(True)

    def on_iconify(self, event):
        self.Hide()
        if self.trayicon is None:
            self.trayicon = RevivingTaskBarIcon(self.Icon,
                                                version.APPNAME,
                                                self)

    def on_close(self, event):
        if self.trayicon:
            self.trayicon.RemoveIcon()
        self.Destroy()
        sys.exit(0)

class Notebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)

        self.config = ConfigPanel(self)
        self.config.SetBackgroundColour("#DFDFDF")
        self.AddPage(self.config, "Configuration")
        
        self.log = LogPanel(self)
        self.log.SetBackgroundColour("#DFDFDF")
        self.AddPage(self.log, "Log")

        self.about = AboutPanel(self)
        self.about.SetBackgroundColour("#DFDFDF")
        self.AddPage(self.about, "About")

class ConfigPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.config = wx.Config(version.APPNAME, version.VENDORNAME)
        self.checkboxes = []
        sizer = wx.BoxSizer(wx.VERTICAL)

        auth_panel = wx.Panel(self)
        auth_sizer = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(auth_panel, label="Auth Token: ",
                           style=wx.TE_DONTWRAP)
        auth_sizer.Add(st, flag=wx.ALL)

        tc = wx.TextCtrl(auth_panel, -1, self.config.Read("auth_token"))
        tc.SetMaxLength(64)
        tc.Bind(wx.EVT_SET_FOCUS, self.auth_got_focus)
        tc.Bind(wx.EVT_KILL_FOCUS, self.auth_lost_focus)
        auth_sizer.Add(tc, flag=wx.ALL | wx.EXPAND, proportion=1)
        auth_panel.SetSizer(auth_sizer)
        self.auth_token = tc
        self.auth_lost_focus(None)
        sizer.Add(auth_panel, flag=wx.ALL | wx.EXPAND, border=5)

        for h in sorted(handler.FILE_HANDLER.values(),
                        key=lambda x: x.display):
            cb = ConfigCheckBox(self, h.method,
                                tooltip=h.description,
                                label=h.display)
            sizer.Add(cb, flag=wx.ALL | wx.EXPAND, border=5)
        self.SetSizer(sizer)

    def auth_got_focus(self, event):
        if self.auth_token:
            self.auth_token.SetBackgroundColour("White")

    def auth_lost_focus(self, event):
        if self.auth_token:
            auth_token = self.auth_token.GetValue()
            self.config.Write("auth_token", auth_token)
            if api.check_auth_token(auth_token):
                self.auth_token.SetBackgroundColour("#AFFFAF")
            else:
                self.auth_token.SetBackgroundColour("#FFAFAF")


class ConfigCheckBox(wx.CheckBox):
    def __init__(self, parent, method, tooltip=None, *args, **kwargs):
        wx.CheckBox.__init__(self, parent, *args, **kwargs)
        if tooltip is not None:
            self.SetToolTip(wx.ToolTip(tooltip))
        self.method = method
        self.config = parent.config
        if self.config.Exists(method):
            self.SetValue(self.config.ReadBool(method))
        else:
            self.SetValue(True)
            self.config.WriteBool(method, True)

        self.Bind(wx.EVT_CHECKBOX, self.toggle)

    def toggle(self, event):
        self.config.WriteBool(self.method, self.GetValue())


class LogPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.logtext = wx.TextCtrl(self, style=(wx.TE_MULTILINE |
                                                wx.TE_READONLY |
                                                wx.TE_RICH))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.logtext, flag=wx.ALL | wx.EXPAND, proportion=1)
        self.SetSizer(sizer)

class AboutPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.text = wx.StaticText(self, style=wx.ALIGN_CENTRE,
                                  label=version.ABOUT)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.text, 
                  flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL,
                  proportion=1)
        self.SetSizer(sizer)

##################################################################
# Hiding in the systray

class RevivingTaskBarIcon(wx.TaskBarIcon):
    def __init__(self, icon, tooltip, frame):
        wx.TaskBarIcon.__init__(self)
        self.SetIcon(icon, tooltip)
        self.frame = frame
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_left_dclick)

    def on_left_dclick(self, e):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
            self.frame.Raise()
        self.frame.trayicon = None
        self.RemoveIcon()

##################################################################
# Logging

def initialize_logging(frame):
    textctrl = frame.notebook.log.logtext
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.INFO)
    gdu_handler = TextCtrlHandler(textctrl)
    gdu_handler.setFormatter(
        # %(asctime)s %(name)-12s %(levelname)-8s
        logging.Formatter('%(asctime)s %(message)s')
        )
    root_logger.addHandler(gdu_handler)

class TextCtrlHandler(logging.Handler):
    def __init__(self, textctrl, *args, **kwargs):
        super(TextCtrlHandler, self).__init__(*args, **kwargs)
        self.textctrl = textctrl

    def emit(self, record):
        if self.textctrl:
            self.textctrl.AppendText(self.format(record) + "\n")
