#!/usr/bin/env python

import os
import time
import wx
import wx.lib.newevent
import numpy as np

# Include pyatari directory so that modules can be imported normally
import sys
module_dir = os.path.realpath(os.path.abspath(".."))
if module_dir not in sys.path:
    sys.path.insert(0, module_dir)
import pyatari800

import logging
logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

KEY_WARMSTART = 2
KEY_COLDSTART = 3

class EmulatorPanel(wx.Panel):
    def __init__(self, parent, emulator):
        self.parent = parent
        self.emulator = emulator
        wx.Panel.__init__(self, parent, -1, size=(emulator.width, emulator.height))

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_CHAR, self.on_char)

        self.firsttime=True
        self.refreshed=False
        self.repeat=True
        self.forceupdate=False
        self.delay = 5  # wxpython delays are in milliseconds

        self.on_size(None)
        if self.IsDoubleBuffered():
            self.Bind(wx.EVT_PAINT, self.on_paint)
        else:
            self.Bind(wx.EVT_PAINT, self.on_paint_double_buffer)
    
    def on_key_down(self, evt):
        log.debug("key down before evt=%s" % evt.GetKeyCode())
        key=evt.GetKeyCode()
        evt.Skip()
    
    def on_key_up(self, evt):
        log.debug("key up before evt=%s" % evt.GetKeyCode())
        key=evt.GetKeyCode()
        evt.Skip()

    def on_char(self, evt):
        log.debug("on_char! char=%s, key=%s, modifiers=%s" % (evt.GetUniChar(), evt.GetKeyCode(), bin(evt.GetModifiers())))
        mods = evt.GetModifiers()
        char = evt.GetUniChar()
        evt.Skip()

    def on_size(self,evt):
        if not self.IsDoubleBuffered():
            # make new background buffer
            size  = self.GetClientSizeTuple()
            self._buffer = wx.EmptyBitmap(*size)

    def updateDrawing(self,dc):
        #dc=wx.BufferedDC(wx.ClientDC(self), self._buffer)
        bmp=self.emulator.get_bitmap()
        dc.DrawBitmap(bmp, 0,0, True)

    def on_paint(self, evt):
        dc=wx.PaintDC(self)
        self.updateDrawing(dc)
        self.refreshed=True

    def on_paint_double_buffer(self, evt):
        dc=wx.BufferedPaintDC(self,self._buffer)
        self.updateDrawing(dc)
        self.refreshed=True

    def on_timer(self, evt):
        if self.timer.IsRunning():
            if self.emulator.is_frame_ready():
                print "ready!"
                if self.forceupdate:
                    dc = wx.ClientDC(self)
                    self.updateDrawing(dc)
                else:
                    #self.updateDrawing()
                    self.Refresh()
                self.emulator.next_frame()
        evt.Skip()

    def start_timer(self,repeat=False,delay=None,forceupdate=True):
        if not self.timer.IsRunning():
            self.repeat=repeat
            if delay is not None:
                self.delay=delay
            self.forceupdate=forceupdate
            self.timer.Start(self.delay)

    def stop_timer(self):
        if self.timer.IsRunning():
            self.timer.Stop()

    def join_process(self):
        self.stop_timer()
        self.emulator.stop_process()



class TestPanel(wx.Panel):
    def __init__(self, parent, log, emulator):
        self.parent=parent
        self.log = log
        wx.Panel.__init__(self, parent, -1)

        self.emulator_control = EmulatorPanel(self, emulator)

        self.buttonbox=wx.BoxSizer(wx.HORIZONTAL)
        b = wx.Button(self, -1, "Start")
        self.Bind(wx.EVT_BUTTON, self.on_start, b)
        self.buttonbox.Add(b, 0, wx.ALIGN_CENTER)
        b = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause, b)
        self.buttonbox.Add(b, 0, wx.ALIGN_CENTER)
        
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.emulator_control, 1, wx.EXPAND)
        self.box.Add(self.buttonbox, 0, wx.EXPAND)

        self.SetSizer(self.box)
        self.Layout()

    def on_start(self,evt):
        self.emulator_control.start_timer(repeat=True,delay=self.emulator_control.delay)

    def on_pause(self,evt):
        self.emulator_control.stop_timer()

    def end_emulation(self):
        self.emulator_control.join_process()


# Not running inside the wxPython demo, so include the same basic
# framework.
class EmulatorApp(wx.App):
    def OnInit(self):
        frame = wx.Frame(None, -1, "wxPython atari800 test", pos=(50,50),
                         size=(200,100), style=wx.DEFAULT_FRAME_STYLE)
        frame.CreateStatusBar()

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(wx.ID_EXIT, "E&xit\tCtrl-Q", "Exit demo")
        self.Bind(wx.EVT_MENU, self.on_menu, item)
        menuBar.Append(menu, "&File")

        self.id_coldstart = wx.NewId()
        menu = wx.Menu()
        item = menu.Append(self.id_coldstart, "Cold Start", "Cold start (power switch off then on)")
        self.Bind(wx.EVT_MENU, self.on_menu, item)
        menuBar.Append(menu, "&Machine")

        frame.SetMenuBar(menuBar)
        frame.Show(True)
        frame.Bind(wx.EVT_CLOSE, self.on_close_frame)

        self.emulator = pyatari800.Atari800()
        self.emulator.multiprocess()
        self.emulator_panel = TestPanel(frame, None, self.emulator)
        frame.SetSize((450, 350))
        self.emulator_panel.SetFocus()
        self.SetTopWindow(frame)
        self.frame = frame
        return True

    def on_menu(self, evt):
        id = evt.GetId()
        if id == wx.ID_EXIT:
            self.emulator_panel.end_emulation()
            self.frame.Close(True)
        elif id == self.id_coldstart:
            self.emulator.send_special_key(KEY_COLDSTART)

    def on_close_frame(self, evt):
        self.emulator_panel.end_emulation()
        evt.Skip()



if __name__ == '__main__':
    app = EmulatorApp()
    app.MainLoop()
