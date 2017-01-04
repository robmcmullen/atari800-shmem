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

KEY_WARMSTART = 2
KEY_COLDSTART = 3

class EmulatorPanel(wx.Panel):
    def __init__(self, parent, emulator):
        self.parent = parent
        self.emulator = emulator
        wx.Panel.__init__(self, parent, -1, size=(emulator.width, emulator.height))
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        self.timer = wx.Timer(self)
        self.delay = .001
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Catch and ignore the erase event that is apparently called
        # automatically.  Found this here:
        # http://mail.python.org/pipermail/python-list/2003-April/158724.html
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.NoOp)

        self.firsttime=True
        self.refreshed=False
        self.repeat=True
        self.forceupdate=False
        self.delay = 0.001

        self.OnSize(None)
        if self.IsDoubleBuffered():
            self.Bind(wx.EVT_PAINT, self.OnPaint)
        else:
            self.Bind(wx.EVT_PAINT, self.OnPaintDoubleBuffer)

    def NoOp(self,evt):
        pass

    def OnSize(self,evt):
        if not self.IsDoubleBuffered():
            # make new background buffer
            size  = self.GetClientSizeTuple()
            self._buffer = wx.EmptyBitmap(*size)

    def updateDrawing(self,dc):
        #dc=wx.BufferedDC(wx.ClientDC(self), self._buffer)
        bmp=self.emulator.get_bitmap()
        dc.DrawBitmap(bmp, 0,0, True)

    def OnPaint(self, evt):
        dc=wx.PaintDC(self)
        self.updateDrawing(dc)
        self.refreshed=True

    def OnPaintDoubleBuffer(self, evt):
        dc=wx.BufferedPaintDC(self,self._buffer)
        self.updateDrawing(dc)
        self.refreshed=True

    def OnIdle(self, evt):
        #print "Idle!"
        if self.refreshed and self.firsttime:
            #self.startTimer()
            self.firsttime=False

    def OnTimer(self, evt):
        if self.timer.IsRunning():
            print "hi"
            self.emulator.wait_for_frame()
            if self.forceupdate:
                dc = wx.ClientDC(self)
                self.updateDrawing(dc)
            else:
                #self.updateDrawing()
                self.Refresh()
            self.emulator.next_frame()

    def startTimer(self,repeat=False,delay=None,forceupdate=True):
        if not self.timer.IsRunning():
            self.repeat=repeat
            if delay is not None:
                self.delay=delay
            self.forceupdate=forceupdate
            self.timer.Start(self.delay)

    def stopTimer(self):
        if self.timer.IsRunning():
            self.timer.Stop()

    def isPlaying(self):
        return self.timer.IsRunning()

    def setFrame(self,frame):
        self.frame=frame
        self.Refresh()


class TestPanel(wx.Panel):
    def __init__(self, parent, log, emulator):
        self.parent=parent
        self.log = log
        wx.Panel.__init__(self, parent, -1)

        self.emulator_control = EmulatorPanel(self, emulator)

        self.buttonbox=wx.BoxSizer(wx.HORIZONTAL)
        b = wx.Button(self, -1, "Start")
        self.Bind(wx.EVT_BUTTON, self.OnPlay, b)
        self.buttonbox.Add(b, 0, wx.ALIGN_CENTER)
        b = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.OnStop, b)
        self.buttonbox.Add(b, 0, wx.ALIGN_CENTER)
        
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.emulator_control, 1, wx.EXPAND)
        self.box.Add(self.buttonbox, 0, wx.EXPAND)

        self.SetSizer(self.box)
        self.Layout()

    def OnPlay(self,evt):
        self.emulator_control.startTimer(repeat=True,delay=self.emulator_control.delay)

    def OnStop(self,evt):
        self.emulator_control.stopTimer()
        
#----------------------------------------------------------------------

def runTest(frame, nb, log, emulator):
    win = TestPanel(nb, log, emulator)
    return win

#----------------------------------------------------------------------

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
        self.Bind(wx.EVT_MENU, self.OnMenu, item)
        menuBar.Append(menu, "&File")

        self.id_coldstart = wx.NewId()
        menu = wx.Menu()
        item = menu.Append(self.id_coldstart, "Cold Start", "Cold start (power switch off then on)")
        self.Bind(wx.EVT_MENU, self.OnMenu, item)
        menuBar.Append(menu, "&Machine")

        frame.SetMenuBar(menuBar)
        frame.Show(True)
        frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        self.emulator = pyatari800.Atari800()
        self.emulator.multiprocess()
        win = runTest(frame, frame, None, self.emulator)
        frame.SetSize((450, 350))
        win.SetFocus()
        self.SetTopWindow(frame)
        self.frame = frame
        return True

    def OnMenu(self, evt):
        id = evt.GetId()
        if id == wx.ID_EXIT:
            self.emulator.stop_process()
            self.frame.Close(True)
        elif id == self.id_coldstart:
            self.emulator.send_special_key(KEY_COLDSTART)

    def OnCloseFrame(self, evt):
        self.emulator.stop_process()
        evt.Skip()



if __name__ == '__main__':
    app = EmulatorApp()
    app.MainLoop()
