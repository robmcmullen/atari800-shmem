#!/usr/bin/env python

import os
import sys
import time
import wx
import wx.lib.newevent
try:
    import wx.glcanvas as glcanvas
    import OpenGL.GL as gl
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False

import numpy as np

# Include pyatari directory so that modules can be imported normally
import sys
module_dir = os.path.realpath(os.path.abspath(".."))
if module_dir not in sys.path:
    sys.path.insert(0, module_dir)
import pyatari800
from pyatari800.akey import *
from pyatari800.shmem import *
from texture_canvas_120 import GLSLTextureCanvas, LegacyTextureCanvas

import logging
logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class EmulatorControlBase(object):
    def __init__(self, emulator, autostart=False):
        self.emulator = emulator

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
        self.screen_scale = 1

        self.key_down = False

        self.on_size(None)
        if self.IsDoubleBuffered():
            self.Bind(wx.EVT_PAINT, self.on_paint)
        else:
            self.Bind(wx.EVT_PAINT, self.on_paint_double_buffer)

        if autostart:
            wx.CallAfter(self.on_start, None)
    
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

        evt.Skip()

    def on_char(self, evt):
        log.debug("on_char! char=%s, key=%s, raw=%s modifiers=%s" % (evt.GetUniChar(), evt.GetKeyCode(), evt.GetRawKeyCode(), bin(evt.GetModifiers())))
        mods = evt.GetModifiers()
        char = evt.GetUniChar()
        if char > 0:
            self.emulator.send_char(char)
        else:
            key = evt.GetKeyCode()

        evt.Skip()

    def process_key_state(self):
        up = 0b0001 if wx.GetKeyState(wx.WXK_UP) else 0
        down = 0b0010 if wx.GetKeyState(wx.WXK_DOWN) else 0
        left = 0b0100 if wx.GetKeyState(wx.WXK_LEFT) else 0
        right = 0b1000 if wx.GetKeyState(wx.WXK_RIGHT) else 0
        self.emulator.exchange_input.joy0 = up | down | left | right
        trig = 1 if wx.GetKeyState(wx.WXK_CONTROL) else 0
        self.emulator.exchange_input.trig0 = trig
        #print "joy", self.emulator.exchange_input.joy0, "trig", trig

        # console keys will reflect being pressed if at any time between frames
        # the key has been pressed
        self.emulator.exchange_input.option = 1 if wx.GetKeyState(wx.WXK_F2) else 0
        self.emulator.exchange_input.select = 1 if wx.GetKeyState(wx.WXK_F3) else 0
        self.emulator.exchange_input.start = 1 if wx.GetKeyState(wx.WXK_F4) else 0

    def on_size(self,evt):
        if not self.IsDoubleBuffered():
            # make new background buffer
            size  = self.GetClientSizeTuple()
            self._buffer = wx.EmptyBitmap(*size)

    def show_frame(self):
        raise NotImplementedError

    def show_audio(self):
        import binascii
        a = binascii.hexlify(self.emulator.audio)
        #print a

    def on_timer(self, evt):
        if self.timer.IsRunning():
            if self.emulator.is_frame_ready():
                self.show_frame()
                self.show_audio()
                self.emulator.next_frame()
            self.process_key_state()
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

    def on_start(self, evt=None):
        self.start_timer(repeat=True)

    @property
    def is_paused(self):
        return not self.timer.IsRunning()

    def on_pause(self, evt=None):
        self.stop_timer()

    def end_emulation(self):
        self.join_process()


class EmulatorControl(wx.Panel, EmulatorControlBase):
    def __init__(self, parent, emulator, autostart=False):
        wx.Panel.__init__(self, parent, -1, size=(emulator.width, emulator.height))
        EmulatorControlBase.__init__(self, emulator, autostart)

    def get_bitmap(self, frame):
        scaled = self.scale_frame(frame)
        h, w, _ = scaled.shape
        image = wx.ImageFromData(w, h, scaled.tostring())
        bmp = wx.BitmapFromImage(image)
        return bmp

    def set_scale(self, scale):
        self.screen_scale = scale
        self.delay = 5 * scale * scale
        newdims = np.asarray((self.emulator.height * scale, self.emulator.width * scale))
        base = np.indices(newdims)
        d = []
        d.append(base[0]/self.screen_scale)
        d.append(base[1]/self.screen_scale)
        cd = np.array(d)
        self.raw_scaled_lookup = list(cd)
        self.stop_timer()
        self.start_timer(True)

    def scale_frame(self, frame):
        if self.screen_scale == 1:
            return frame
        scaled = frame[self.raw_scaled_lookup]
        print "panel scale: %d, %s" % (self.screen_scale, scaled.shape)
        return scaled

    def show_frame(self):
        if self.forceupdate:
            dc = wx.ClientDC(self)
            self.updateDrawing(dc)
        else:
            #self.updateDrawing()
            self.Refresh()

    def updateDrawing(self,dc):
        #dc=wx.BufferedDC(wx.ClientDC(self), self._buffer)
        frame = self.emulator.get_frame(self.screen_scale)
        bmp = self.get_bitmap(frame)
        dc.DrawBitmap(bmp, 0,0, True)

    def on_paint(self, evt):
        dc=wx.PaintDC(self)
        self.updateDrawing(dc)
        self.refreshed=True

    def on_paint_double_buffer(self, evt):
        dc=wx.BufferedPaintDC(self,self._buffer)
        self.updateDrawing(dc)
        self.refreshed=True


class OpenGLEmulatorMixin(object):
    def bind_events(self):
        pass

    def get_raw_texture_data(self, raw=None):
        print "RAW!"
        raw = np.flipud(self.emulator.raw.reshape((240, 336)))
        return raw

    def show_frame(self):
        if not self.finished_init:
            return
        frame = self.calc_texture_data()
        try:
            self.update_texture(self.display_texture, frame)
        except Exception, e:
            import traceback

            print traceback.format_exc()
            sys.exit()
        self.on_draw()

    def on_paint(self, evt):
        print "here"
        if not self.finished_init:
            print "here1"
            self.init_context()
        self.show_frame()

    on_paint_double_buffer = on_paint


class OpenGLEmulatorControl(OpenGLEmulatorMixin, LegacyTextureCanvas, EmulatorControlBase):
    def __init__(self, parent, emulator, autostart=False):
        LegacyTextureCanvas.__init__(self, parent, -1, size=(3*emulator.width, 3*emulator.height))
        EmulatorControlBase.__init__(self, emulator, autostart)
        emulator.set_scale(1, use_alpha=True)

    def get_raw_texture_data(self, raw=None):
        raw = np.flipud(self.emulator.get_frame())
        print "raw data for legacy version:", raw.shape
        return raw


class GLSLEmulatorControl(OpenGLEmulatorMixin, GLSLTextureCanvas, EmulatorControlBase):
    def __init__(self, parent, emulator, autostart=False):
        GLSLTextureCanvas.__init__(self, parent, -1, size=(3*emulator.width, 3*emulator.height))
        EmulatorControlBase.__init__(self, emulator, autostart)


# Not running inside the wxPython demo, so include the same basic
# framework.
class EmulatorApp(wx.App):
    parsed_args = []
    options = {}

    def OnInit(self):
        frame = wx.Frame(None, -1, "wxPython atari800 test", pos=(50,50),
                         size=(200,100), style=wx.DEFAULT_FRAME_STYLE)
        frame.CreateStatusBar()

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(wx.ID_EXIT, "E&xit\tCtrl-Q", "Exit demo")
        self.Bind(wx.EVT_MENU, self.on_menu, item)
        menuBar.Append(menu, "&File")

        self.id_pause = wx.NewId()
        self.id_coldstart = wx.NewId()
        self.id_warmstart = wx.NewId()
        menu = wx.Menu()
        self.pause_item = menu.Append(self.id_pause, "Pause", "Pause or resume the emulation")
        self.Bind(wx.EVT_MENU, self.on_menu, self.pause_item)
        menu.AppendSeparator()
        item = menu.Append(self.id_coldstart, "Cold Start", "Cold start (power switch off then on)")
        self.Bind(wx.EVT_MENU, self.on_menu, item)
        item = menu.Append(self.id_coldstart, "Warm Start", "Warm start (reset switch)")
        self.Bind(wx.EVT_MENU, self.on_menu, item)
        menuBar.Append(menu, "&Machine")

        self.id_screen1x = wx.NewId()
        self.id_screen2x = wx.NewId()
        menu = wx.Menu()
        item = menu.Append(self.id_screen1x, "Display 1x", "No magnification")
        self.Bind(wx.EVT_MENU, self.on_menu, item)
        item = menu.Append(self.id_screen2x, "Display 2x", "2x display")
        self.Bind(wx.EVT_MENU, self.on_menu, item)
        menuBar.Append(menu, "&Screen")

        frame.SetMenuBar(menuBar)
        frame.Show(True)
        frame.Bind(wx.EVT_CLOSE, self.on_close_frame)

        self.emulator = pyatari800.Atari800(self.parsed_args)
        self.emulator.multiprocess()
        if self.options.glsl and HAS_OPENGL:
            control = GLSLEmulatorControl
        elif self.options.opengl and HAS_OPENGL:
            control = OpenGLEmulatorControl
        else:
            control = EmulatorControl
        self.emulator_panel = control(frame, self.emulator, autostart=True)
        frame.SetSize((800, 600))
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
        elif id == self.id_warmstart:
            self.emulator.send_special_key(AKEY_WARMSTART)
        elif id == self.id_screen1x:
            self.emulator_panel.set_scale(1)
        elif id == self.id_screen2x:
            self.emulator_panel.set_scale(2)
        elif id == self.id_pause:
            if self.emulator_panel.is_paused:
                self.emulator_panel.on_start()
                self.pause_item.SetItemLabel("Pause")
            else:
                self.emulator_panel.on_pause()
                self.pause_item.SetItemLabel("Resume")


    def on_close_frame(self, evt):
        self.emulator_panel.end_emulation()
        evt.Skip()



if __name__ == '__main__':
    # use argparse rather than sys.argv to handle the difference in being
    # called as "python script.py" and "./script.py"
    import argparse

    parser = argparse.ArgumentParser(description='Atari800 WX Demo')
    parser.add_argument("--bitmap", action="store_false", dest="opengl", default=True, help="Use bitmap scaling instead of OpenGL")
    parser.add_argument("--opengl", action="store_true", dest="opengl", default=True, help="Use OpenGL scaling")
    parser.add_argument("--glsl", action="store_true", dest="glsl", default=False, help="Use GLSL scaling")
    EmulatorApp.options, EmulatorApp.parsed_args = parser.parse_known_args()
    app = EmulatorApp()
    app.MainLoop()
