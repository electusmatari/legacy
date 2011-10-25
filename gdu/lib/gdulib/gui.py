#!/usr/bin/env python

import logging
import sys
import webbrowser
import _winreg

import wx
import wx.html

from gdulib import rpc
from gdulib import handler
from gdulib import version

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None,
                          title='Gradient Data Uploader',
                          size=(640, 480),
                          style=wx.ICONIZE | wx.DEFAULT_FRAME_STYLE)
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
                                                version.APPLONGNAME,
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
        # self.config.SetBackgroundColour("#DFDFDF")
        self.AddPage(self.config, "Configuration")
        
        self.log = LogPanel(self)
        # self.log.SetBackgroundColour("#DFDFDF")
        self.AddPage(self.log, "Log")

        self.about = AboutPanel(self)
        self.AddPage(self.about, "About")

class ConfigPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.config = wx.Config(version.APPLONGNAME, version.VENDORNAME)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.init_auth_panel(), flag=wx.ALL | wx.EXPAND, border=5)
        sizer.Add(self.init_method_panel(), flag=wx.ALL | wx.EXPAND, border=5)
        sizer.Add(self.init_other_panel(), flag=wx.ALL | wx.EXPAND, border=5)
        self.SetSizer(sizer)

    def init_auth_panel(self):
        panel = wx.Panel(self)
        sb = wx.StaticBox(panel, label="Authentication")
        sizer = wx.StaticBoxSizer(sb, wx.HORIZONTAL)

        st = wx.StaticText(panel, label="Auth Token: ",
                           style=wx.TE_DONTWRAP)
        sizer.Add(st, flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL,
                  border=5)

        tc = wx.TextCtrl(panel, -1, self.config.Read("auth_token"))
        self.auth_token = tc
        self.auth_token_ok = False
        self.auth_lost_focus(None) # initialize color
        tc.SetMaxLength(64)
        tc.Bind(wx.EVT_SET_FOCUS, self.auth_got_focus)
        tc.Bind(wx.EVT_KILL_FOCUS, self.auth_lost_focus)
        sizer.Add(tc, flag=wx.ALL | wx.EXPAND, proportion=1)

        checkb = wx.Button(panel, label="Check")
        checkb.Bind(wx.EVT_BUTTON, self.on_check)
        sizer.Add(checkb, flag=wx.ALL)

        getb = wx.Button(panel, label="Get Your Token")
        getb.Bind(wx.EVT_BUTTON, self.on_get)
        sizer.Add(getb, flag=wx.ALL)

        panel.SetSizer(sizer)
        return panel

    def init_method_panel(self):
        panel = wx.Panel(self)
        sb = wx.StaticBox(panel, label="Data Uploads")
        sizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        self.checkboxes = []
        for h in sorted(handler.FILE_HANDLER.values(),
                        key=lambda x: x.display):
            cb = ConfigCheckBox(panel, h.method, self.config,
                                label=h.display,
                                tooltip=h.description)
            sizer.Add(cb, flag=wx.ALL | wx.EXPAND, border=2)
            self.checkboxes.append(cb)
        panel.SetSizer(sizer)
        return panel

    def init_other_panel(self):
        panel = wx.Panel(self)
        sb = wx.StaticBox(panel, label="Miscellaneous Options")
        sizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        cb = AutostartCheckBox(panel, version.APPLONGNAME,
                               label="Autostart on Windows log-in",
                               tooltip=("Automatically start when the "
                                        "current user logs in"))
        sizer.Add(cb, flag=wx.ALL | wx.EXPAND, border=2)
        cb = ConfigCheckBox(panel, 'show_all_rpc_calls', self.config,
                            default=False,
                            label='Show all RPC calls',
                            tooltip=("Show all RPC calls as they happen; "
                                     "mostly of technical interest"))
        self.show_all_rpc_calls = cb
        sizer.Add(cb, flag=wx.ALL | wx.EXPAND, border=2)
        panel.SetSizer(sizer)
        return panel

    def auth_got_focus(self, event):
        if self.auth_token:
            self.auth_token.SetBackgroundColour("White")
            self.auth_token.SetSelection(-1, -1)

    def auth_lost_focus(self, event, do_notify=False):
        if self.auth_token:
            auth_token = self.auth_token.GetValue()
            self.config.Write("auth_token", auth_token)
            if rpc.check_auth_token(auth_token):
                self.auth_token.SetBackgroundColour("#AFFFAF")
                self.auth_token_ok = True
            else:
                self.auth_token.SetBackgroundColour("#FFAFAF")
                self.auth_token_ok = False

    def on_check(self, event):
        self.auth_lost_focus(event)

    def on_get(self, event):
        webbrowser.open(version.AUTH_TOKEN_URL,
                        new=2 # New Tab
                        )


class ConfigCheckBox(wx.CheckBox):
    def __init__(self, parent, option, config, default=True,
                 tooltip=None, *args, **kwargs):
        wx.CheckBox.__init__(self, parent, *args, **kwargs)
        if tooltip is not None:
            self.SetToolTip(wx.ToolTip(tooltip))
        self.option = option
        self.config = config
        if self.config.Exists(option):
            self.SetValue(self.config.ReadBool(option))
        else:
            self.SetValue(default)
            self.config.WriteBool(option, default)

        self.Bind(wx.EVT_CHECKBOX, self.toggle)

    def toggle(self, event):
        self.config.WriteBool(self.option, self.GetValue())


class AutostartCheckBox(wx.CheckBox):
    def __init__(self, parent, appname,
                 tooltip=None, *args, **kwargs):
        wx.CheckBox.__init__(self, parent, *args, **kwargs)
        if tooltip is not None:
            self.SetToolTip(wx.ToolTip(tooltip))
        self.appname = appname
        self.registry = _winreg.ConnectRegistry(None,
                                                _winreg.HKEY_CURRENT_USER)
        if self.get_autostart():
            self.SetValue(True)
        else:
            self.SetValue(False)
        self.Bind(wx.EVT_CHECKBOX, self.toggle)

    def toggle(self, event):
        self.set_autostart(self.GetValue())

    def regkey(self):
        return _winreg.OpenKey(
            self.registry,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            _winreg.KEY_ALL_ACCESS)

    def get_autostart(self):
        with self.regkey() as key:
            try:
                _winreg.QueryValueEx(key, self.appname)
                return True
            except WindowsError:
                return False

    def set_autostart(self, do_autostart):
        with self.regkey() as key:
            if do_autostart:
                _winreg.SetValueEx(key, self.appname, 0, _winreg.REG_SZ,
                                   sys.executable)
            else:
                try:
                    _winreg.DeleteValue(key, self.appname)
                except WindowsError:
                    pass


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
        html = wxHTML(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, flag=wx.ALL|wx.EXPAND, proportion=1)
        self.SetSizer(sizer)
        html.SetPage(version.ABOUTHTML)

class wxHTML(wx.html.HtmlWindow):
    def OnLinkClicked(self, link):
        webbrowser.open(link.GetHref(), new=2)

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
