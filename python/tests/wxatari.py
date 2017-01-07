#!/usr/bin/env python

import os
import sys
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
from pyatari800.akey import *
from pyatari800.shmem import *

import logging
logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


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

        self.key_down = False

        self.on_size(None)
        if self.IsDoubleBuffered():
            self.Bind(wx.EVT_PAINT, self.on_paint)
        else:
            self.Bind(wx.EVT_PAINT, self.on_paint_double_buffer)
    
    wx_to_akey = {
        wx.WXK_BACK: AKEY_BACKSPACE,
        wx.WXK_DELETE: AKEY_DELETE_CHAR,
        wx.WXK_INSERT: AKEY_INSERT_CHAR,
        wx.WXK_ESCAPE: AKEY_ESCAPE,
        wx.WXK_END: AKEY_HELP,
        wx.WXK_HOME: AKEY_CLEAR,
        wx.WXK_RETURN: AKEY_RETURN,
        wx.WXK_SPACE: AKEY_SPACE,
        wx.WXK_F7: AKEY_BREAK,
        wx.WXK_PAUSE: AKEY_BREAK,
        96: AKEY_ATARI,  # back tick
    }

    wx_to_akey_ctrl = {
        wx.WXK_UP: AKEY_UP,
        wx.WXK_DOWN: AKEY_DOWN,
        wx.WXK_LEFT: AKEY_LEFT,
        wx.WXK_RIGHT: AKEY_RIGHT,
    }

    def on_key_down(self, evt):
        log.debug("key down! key=%s mod=%s" % (evt.GetKeyCode(), evt.GetModifiers()))
        key = evt.GetKeyCode()
        mod = evt.GetModifiers()
        if mod == wx.MOD_CONTROL:
            akey = self.wx_to_akey_ctrl.get(key, None)
        else:
            akey = self.wx_to_akey.get(key, None)

        if akey is None:
            evt.Skip()
        else:
            self.emulator.send_keycode(akey)
    
    def on_key_up(self, evt):
        log.debug("key up before evt=%s" % evt.GetKeyCode())
        key=evt.GetKeyCode()
        self.emulator.clear_keys()

        if key == wx.WXK_F2:
            self.emulator.set_option(0)
        if key == wx.WXK_F3:
            self.emulator.set_select(0)
        if key == wx.WXK_F4:
            self.emulator.set_start(0)

        evt.Skip()

    def on_char(self, evt):
        log.debug("on_char! char=%s, key=%s, raw=%s modifiers=%s" % (evt.GetUniChar(), evt.GetKeyCode(), evt.GetRawKeyCode(), bin(evt.GetModifiers())))
        mods = evt.GetModifiers()
        char = evt.GetUniChar()
        if char > 0:
            self.emulator.send_char(char)
        else:
            key = evt.GetKeyCode()
            if key == wx.WXK_F2:
                self.emulator.set_option(1)
            if key == wx.WXK_F3:
                self.emulator.set_select(1)
            if key == wx.WXK_F4:
                self.emulator.set_start(1)

        evt.Skip()

    def process_key_presses(self):
        up = 0b0001 if wx.GetKeyState(wx.WXK_UP) else 0
        down = 0b0010 if wx.GetKeyState(wx.WXK_DOWN) else 0
        left = 0b0100 if wx.GetKeyState(wx.WXK_LEFT) else 0
        right = 0b1000 if wx.GetKeyState(wx.WXK_RIGHT) else 0
        self.emulator.exchange[input_joy0] = up | down | left | right
        trig = 1 if wx.GetKeyState(wx.WXK_CONTROL) else 0
        self.emulator.exchange[input_trig0] = trig
        #print "joy", self.emulator.exchange[input_joy0], "trig", trig

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
                if self.forceupdate:
                    dc = wx.ClientDC(self)
                    self.updateDrawing(dc)
                else:
                    #self.updateDrawing()
                    self.Refresh()
                self.emulator.next_frame()
            self.process_key_presses()
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
    parsed_args = []

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

        self.emulator = pyatari800.Atari800(self.parsed_args)
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
            self.emulator.send_special_key(AKEY_COLDSTART)

    def on_close_frame(self, evt):
        self.emulator_panel.end_emulation()
        evt.Skip()



if __name__ == '__main__':
    # use argparse rather than sys.argv to handle the difference in being
    # called as "python script.py" and "./script.py"
    import argparse

    parser = argparse.ArgumentParser(description='Atari800 WX Demo')
    EmulatorApp.parsed_args = parser.parse_known_args()[1]
    app = EmulatorApp()
    app.MainLoop()
