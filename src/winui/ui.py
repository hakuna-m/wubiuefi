#
# Copyright (c) 2007, 2008 Agostino Russo
#
# Written by Agostino Russo <agostino.russo@gmail.com>
#
# win32.ui is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# win32.ui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

'''
Python wrappers around win32 widgets and window classes
'''

import defs
import sys
import os
import ctypes

__all__ = ["Window", "Frontend"]

#TBD use weakref in _event_handlers_
_event_handlers_ = {}

if sys.version.startswith('2.3'):
    from sets import Set as set

def event_dispatcher(hwnd, message, wparam, lparam):
    eh = _event_handlers_
    na = {}
    nas = set()
    handlers = set()
    for eh in [eh.get(hwnd, na), eh.get(None, na)]:
        for eh in [eh.get(message, na) , eh.get(None, na)]:
            for eh in [eh.get(wparam, na) , eh.get(None, na)]:
                handlers |= eh.get(lparam, nas)
                handlers |= eh.get(None, nas)
    for obj, handler_name in handlers:
        handler = getattr(obj, handler_name, None)
        if not callable(handler): continue
        result = handler((hwnd, message, wparam, lparam))
        if bool(result):
            return result
    return ctypes.wintypes.windll.user32.DefWindowProcW(
        ctypes.c_int(hwnd),
        ctypes.c_int(message),
        ctypes.c_int(wparam),
        ctypes.c_int(lparam))

def event_handler(hwnd=None, message=None, wparam=None, lparam=None):
    '''
    Decorator for event handlers
    The handler must return True to stop further message processing by other handlers of the same Window
    '''
    def decorator(func):
        func._handled_event_ = (hwnd, message, wparam, lparam)
        return func
    return decorator

class BasicWindow(object):
    '''
    Wraps
    '''
    _window_class_name_ = None
    _window_class_style_ = defs.CS_HREDRAW | defs.CS_VREDRAW
    _window_style_ = 0
    _window_ex_style_ = 0

    def __init__(self, parent=None, x=None, y=None, width=None, height=None, text=None, frontend=None, icon=None):
        self.parent = parent
        self._icon = None
        if frontend:
            self.frontend = frontend
        else:
            self.frontend = parent.frontend
        if not self.__class__._window_class_name_:
            self.__class__._window_class_name_ = self.__class__.__name__
            if icon:
                self._icon = ctypes.wintypes.windll.user32.LoadImageW(defs.NULL, unicode(icon, 'mbcs'), defs.IMAGE_ICON, 0, 0, defs.LR_LOADFROMFILE);
            self._register_window()
        self._create_window(x, y, width, height, text)
        self._register_handlers()
        self.on_init()

    def _register_window(self):
        self._window_class_ = defs.WNDCLASSEX(
                event_dispatcher,
                self._window_class_name_,
                self._window_class_style_,
                icon=self._icon)
        self._window_class_._atom_ = ctypes.wintypes.windll.user32.RegisterClassExW(ctypes.byref(self._window_class_))
        if not self._window_class_._atom_:
            raise ctypes.wintypes.WinError()

    def _create_window(self, x=None, y=None, width=None, height=None, text=None):
        hmenu = defs.NULL
        lpparam = defs.NULL
        hwnd = self.parent and self.parent._hwnd or defs.NULL
        frontend_hinstance = self.frontend._hinstance
        if x is None:
            x = defs.CW_USEDEFAULT
        if y is None:
            y = defs.CW_USEDEFAULT
        if width is None:
            width = defs.CW_USEDEFAULT
        if height is None:
            height = defs.CW_USEDEFAULT
        if not text:
            text = ""
        self._hwnd = defs.CreateWindowEx(
            self._window_ex_style_,
            unicode(self._window_class_name_),
            unicode(text),
            self._window_style_,
            x, y, width, height,
            hwnd,
            hmenu,
            frontend_hinstance,
            lpparam)

    def _register_handlers(self):
        for key in dir(self):
            handler = getattr(self, key)
            handled_event = getattr(handler, "_handled_event_", None)
            if callable(handler) and handled_event:
                handled_event = list(handled_event)
                for i,subkey in enumerate(handled_event):
                    if subkey is defs.SELF_HWND:
                        handled_event[i] = self._hwnd
                    elif subkey is defs.PARENT_HWND:
                        handled_event[i] = self.parent._hwnd
                    elif subkey is defs.APPLICATION_HINSTANCE:
                        handled_event[i] = self.frontend._hinstance
                self._add_event_handler(key , handled_event)

    def _add_event_handler(self, handler_name, handled_event):
        hwnd, message, wparam, lparam = handled_event
        eh = _event_handlers_
        eh = eh.setdefault(hwnd,{})
        eh = eh.setdefault(message,{})
        eh = eh.setdefault(wparam,{})
        handlers = eh.setdefault(lparam,set())
        handlers.add((self, handler_name))

    def on_init(self):
        pass

class Window(BasicWindow):
    _repaint_on_move_ = False
    _is_transparent_ = False

    def __init__(self, parent=None, x=None, y=None, width=None, height=None, text=None, frontend=None, icon=None):
        self._gdi_disposables = []
        self._background_color = None
        self._background_brush = None
        self._default_background_brush = None
        self._text_color = None
        self._null_brush = ctypes.wintypes.windll.gdi32.GetStockObject(defs.NULL_BRUSH)
        self._gdi_disposables.append(self._null_brush)
        BasicWindow.__init__(self, parent, x, y, width, height, text, frontend, icon)
        self.set_font()
        self.update()

    def get_window_rect(self):
        rect = ctypes.wintypes.RECT()
        ctypes.wintypes.windll.user32.GetWindowRect(self._hwnd, ctypes.byref(rect))
        return rect.left, rect.top, rect.right, rect.bottom

    def get_client_rect(self):
        rect = ctypes.wintypes.RECT()
        ctypes.wintypes.windll.user32.GetClientRect(self._hwnd, ctypes.byref(rect))
        return rect.left, rect.top, rect.right, rect.bottom

    def move(self, x, y):
        if not ctypes.wintypes.windll.user32.SetWindowPos(self._hwnd, defs.NULL, x, y, 0, 0,  defs.SWP_NOSIZE):
        #~ if not windll.user32.MoveWindow(self._hwnd, x, y, -1, -1, self._repaint_on_move_): #repaint
            raise ctypes.wintypes.WinError()

    def resize(self, width, height):
        if not ctypes.wintypes.windll.user32.SetWindowPos(self._hwnd, defs.NULL, 0, 0, width, height, defs.SWP_NOMOVE):
            raise ctypes.wintypes.WinError()

    def show(self):
        #http://msdn.microsoft.com/en-us/library/ms633548.aspx
        self.on_show()
        if not ctypes.wintypes.windll.user32.ShowWindow(self._hwnd, defs.SW_SHOWNORMAL):
            #raise WinError()
            pass
        self.update()

    def enable(self):
        if not ctypes.wintypes.windll.user32.EnableWindow(self._hwnd, True):
            #raise WinError()
            pass
        self.update()

    def disable(self):
        if not ctypes.wintypes.windll.user32.EnableWindow(self._hwnd, False):
            #raise WinError()
            pass
        self.update()

    def hide(self):
        if not ctypes.wintypes.windll.user32.ShowWindow(self._hwnd, defs.SW_HIDE):
            #~ raise WinError()
            pass

    def set_focus(self):
        ctypes.wintypes.windll.user32.SetFocus(self._hwnd)

    def update(self, full=False):
        if full:
            ctypes.wintypes.windll.user32.ShowWindow(self._hwnd, defs.SW_HIDE)
            ctypes.wintypes.windll.user32.ShowWindow(self._hwnd, defs.SW_SHOW)
        if not ctypes.wintypes.windll.user32.UpdateWindow(self._hwnd):
            raise ctypes.wintypes.WinError()

    def get_text(self):
        buffer_max_len = 999
        buffer = (ctypes.c_wchar * buffer_max_len)()
        if ctypes.wintypes.windll.user32.GetWindowTextW(self._hwnd, ctypes.byref(buffer), buffer_max_len):
            return unicode(buffer.value)

    def set_text(self, text):
        old_text = self.get_text()
        if not ctypes.wintypes.windll.user32.SetWindowTextW(self._hwnd, unicode(text)):
            raise ctypes.wintypes.WinError()
        if old_text and old_text.rstrip() != text.rstrip():
            # without update, text is displayed on top of old text when background is transparent
            # TBD check _on_ctlcolorstatic whether that can be avoided
            self.update(full=True)

    def set_font(self, family='Tahoma', size=13, bold=False):
        weight = bold and defs.FW_BOLD or defs.FW_NORMAL
        font = ctypes.wintypes.windll.gdi32.CreateFontW(
            size, # height of font
            0, # average character width
            0, # angle of escapement
            0, # base-line orientation angle
            weight, # font weight
            0, # FALSE italic attribute option
            0, # FALSE underline attribute option
            0, # FALSE strikeout attribute option
            0, # DEFAULT_CHARSET character set identifier
            0, # OUT_DEFAULT_PRECIS output precision
            0, # CLIP_DEFAULT_PRECIS clipping precision
            0, # NONANTIALIASED_QUALITY output quality
            0, #0x20, DEFAULT_PITCH | FF_DONTCARE # pitch and family
            unicode(family) #TEXT("Verdana") # typeface name
            )
        self._gdi_disposables.append(font)
        self._send_message(defs.WM_SETFONT, font, True)

    def set_background_color(self, red255=None, green255=None, blue255=None):
        if (red255, green255, blue255) == (None, None, None):
            self._background_color = None
            if self._default_background_brush:
                ctypes.wintypes.windll.user32.SetClassLongW(self._hwnd, defs.GCL_HBRBACKGROUND, self._default_background_brush)
        else:
            self._background_color = defs.RGB(red255, blue255, green255)
            self._background_brush = ctypes.wintypes.windll.gdi32.CreateSolidBrush(self._background_color)
            self._default_background_brush = ctypes.wintypes.windll.user32.SetClassLongW(self._hwnd, defs.GCL_HBRBACKGROUND, self._background_brush)
            self._gdi_disposables.append(self._background_color)
            self._gdi_disposables.append(self._background_brush)
            self._gdi_disposables.append(self._default_background_brush)

    def set_text_color(self, red255=None, green255=None, blue255=None):
        if (red255, green255, blue255) == (None, None, None):
            self._text_color = None
        else:
            self._text_color = defs.RGB(red255, green255, blue255)
            self._gdi_disposables.append(self._text_color)

    def set_transparency(self, transparent):
        self.is_transparent = transparent
        self.update(full = True)

    def _on_command(self, event):
        self.on_command(event)
    _on_command = event_handler(message=defs.WM_COMMAND, lparam=defs.SELF_HWND)(_on_command)

    def on_command(self, event):
        pass

    def stop_redraw(self):
        self._send_message(defs.WM_SETREDRAW, False, 0)
        #~ LockWindowUpdate(self._hwnd)
        #~ LockWindowUpdate(NULL)

    def start_redraw(self):
        self._send_message(defs.WM_SETREDRAW, True, 0)

    def _send_message(self, message, wparam=0, lparam=0):
        return ctypes.wintypes.windll.user32.SendMessageW(self._hwnd, message, wparam, lparam)

    def _on_destroy(self, event):
        for x in self._gdi_disposables:
            try:
                ctypes.wintypes.windll.gdi32.DeleteObject(x)
            except:
                pass
        self.on_destroy()
    _on_destroy = event_handler(message=defs.WM_DESTROY, hwnd=defs.SELF_HWND)(_on_destroy)

    def _on_ctlcolorstatic(self, event):
        hdc = event[2]
        if self._text_color:
            ctypes.wintypes.windll.gdi32.SetTextColor(hdc, self._text_color)
        if self._is_transparent_:
            ctypes.wintypes.windll.gdi32.SetBkMode(hdc, defs.TRANSPARENT)
            brush = self._null_brush
        else:
            brush = True
        return brush
    event_handler(message=defs.WM_CTLCOLORBTN, lparam=defs.SELF_HWND)(_on_ctlcolorstatic)
    event_handler(message=defs.WM_CTLCOLORSTATIC, lparam=defs.SELF_HWND)(_on_ctlcolorstatic)

    def on_show(self):
        pass

    def on_destroy(self):
        pass

class Frontend(object):
    '''
    Wraps a Windows application
    It is associated to a main window
    It controls the message processing
    '''
    _main_window_class_ = Window

    def __init__(self, main_window_class=None, **kargs):
        self._hwnd = None
        self._hinstance = ctypes.wintypes.windll.kernel32.GetModuleHandleW(ctypes.c_int(defs.NULL))
        kargs["frontend"] = self
        if not main_window_class:
            main_window_class = self._main_window_class_
        self.main_window = main_window_class(**kargs)
        self.on_init()

    def set_title(self, title):
        self.main_window.set_text(title)

    def set_icon(self, icon_path):
        if icon_path and os.path.isfile(icon_path):
            self.main_window._icon = ctypes.wintypes.windll.user32.LoadImageW(defs.NULL, icon_path, defs.IMAGE_ICON, 0, 0, defs.LR_LOADFROMFILE);
            ctypes.wintypes.windll.user32.SendMessageW(self.main_window._hwnd, defs.WM_SETICON, defs.ICON_SMALL, self.main_window._icon)

    def get_title(self):
        return self.main_window.get_text()

    def run(self):
        '''
        Starts the message processing
        '''
        msg = ctypes.wintypes.MSG()
        pMsg = ctypes.pointer(msg)
        self._keep_running = True
        self.on_run()
        while self._keep_running and ctypes.wintypes.windll.user32.GetMessageW(pMsg, defs.NULL, 0, 0) > 0:
            #TBD if IsDialogMessage is used, other messages are not processed, for now doing a manual exception
            if self.main_window._hwnd == defs.NULL \
            or pMsg.contents.message in (defs.WM_COMMAND, defs.WM_PAINT, defs.WM_CTLCOLORSTATIC, defs.WM_DESTROY, defs.WM_QUIT) \
            or not ctypes.wintypes.windll.user32.IsDialogMessage(self.main_window._hwnd , pMsg):
                ctypes.wintypes.windll.user32.TranslateMessage(pMsg)
                ctypes.wintypes.windll.user32.DispatchMessageW(pMsg)

    def stop(self):
        '''
        Stops the message processing
        '''
        self._keep_running = False
        #Post a message to unblock GetMessageW
        ctypes.wintypes.windll.user32.PostMessageW(self.main_window._hwnd, defs.WM_NULL, 0, 0)

    def on_init(self):
        pass

    def on_run(self):
        pass

    def quit(self):
        '''
        Destroys the main window
        '''
        ctypes.wintypes.windll.user32.DestroyWindow(self.main_window._hwnd)

    def _quit(self):
        '''
        Really quit anything on the windows side,
        this is called by MainWindow.on_destroy
        '''
        ctypes.wintypes.windll.user32.PostQuitMessage(0)
        self.on_quit()

    def on_quit(self):
        pass

    def show_error_message(self, message, title=None):
        if not title:
            title = self.get_title()
        ctypes.wintypes.windll.user32.MessageBoxW(self.main_window._hwnd, unicode(message), unicode(title), defs.MB_OK|defs.MB_ICONERROR)

    def show_info_message(self, message, title=None):
        if not title:
            title = self.get_title()
        ctypes.wintypes.windll.user32.MessageBoxW(self.main_window._hwnd, unicode(message), unicode(title), defs.MB_OK|defs.MB_ICONINFORMATION)

    def ask_confirmation(self, message, title=None):
        if not title:
            title = self.get_title()
        result = ctypes.wintypes.windll.user32.MessageBoxW(self.main_window._hwnd, unicode(message), unicode(title), defs.MB_YESNO|defs.MB_ICONQUESTION)
        return result == defs.IDYES

    def ask_to_retry(self, message, title=None):
        if not title:
            title = self.get_title()
        result = ctypes.wintypes.windll.user32.MessageBoxW(self.main_window._hwnd, unicode(message), unicode(title), defs.MB_RETRYCANCEL)
        return result == defs.IDRETRY

class MainWindow(Window):
    '''
    Main Window
    Has borders, and is overlapped, when it is closed, the frontend quits
    '''

    _window_class_name_ = None
    _window_style_ = defs.WS_OVERLAPPEDWINDOW
    _window_ex_style_ = defs.WS_EX_CONTROLPARENT

    def on_destroy(self):
        self.frontend._quit()

    def __del__(self):
        self.frontend._quit()

class MainDialogWindow(MainWindow):
    '''
    Like MainWindow
    But cannot be resized, looks like a dialog
    '''
    _window_style_ =  defs.WS_BORDER |  defs.WS_SYSMENU | defs.WS_CAPTION

class Widget(Window):
    _window_class_name_ = "Must Override This"
    _window_style_ = defs.WS_CHILD | defs.WS_VISIBLE | defs.WS_TABSTOP
    _window_ex_style_ = 0

class StaticWidget(Widget):
    _window_class_name_ = "STATIC"
    _window_style_ = defs.WS_CHILD | defs.WS_VISIBLE
    _window_ex_style_ = defs.WS_EX_TRANSPARENT
    _is_transparent_ = True

class EtchedRectangle(Widget):
    _window_class_name_ = "STATIC"
    _window_style_ = defs.WS_CHILD | defs.WS_VISIBLE | defs.SS_ETCHEDFRAME

class Panel(Window):
    _window_class_name_ = None
    _window_style_ = defs.WS_CHILD | defs.WS_VISIBLE
    _window_ex_style_ = defs.WS_EX_CONTROLPARENT
    #_window_style_ = StaticWidget._window_style_|WS_BORDER

class Edit(Widget):
    _window_class_name_ = "EDIT"
    _window_style_ = Widget._window_style_ | defs.WS_TABSTOP
    _window_ex_style_ = defs.WS_EX_CLIENTEDGE

class PasswordEdit(Widget):
    _window_class_name_ = "EDIT"
    _window_style_ = Widget._window_style_ | defs.ES_PASSWORD | defs.WS_TABSTOP
    _window_ex_style_ = defs.WS_EX_CLIENTEDGE

class Tab(Widget):
    #define WC_TABCONTROLW          L"SysTabControl32"   ???
    _window_class_name_ = "SysTabControl32"

    def add_item(self, title, child, position=0):
        item = defs.TCITEM()
        item.mask = defs.TCIF_TEXT | defs.TCIF_PARAM
        item.pszText = unicode(title)
        item.lParam = child._hwnd
        #~ self.InsertItem(index, item)
        #~ self._ResizeChild(child)
        #~ self.SetCurrentTab(index)
        self._send_message(defs.TCM_INSERTITEM, position, ctypes.byref(item))

class Tooltip(Widget):
    _window_class_name_ = u"SysTabControl32"


class ListBox(Widget):
    _window_class_name_ = "ListBox"
    _window_style_ = Widget._window_style_  | defs.WS_TABSTOP

    def add_item(self, text):
        self._send_message(defs.LB_ADDSTRING, 0, unicode(text))

class ComboBox(Widget):
    _window_class_name_ = "COMBOBOX" #"ComboBoxEx32"
    _window_style_ = Widget._window_style_ | defs.CBS_DROPDOWNLIST | defs.WS_VSCROLL | defs.WS_TABSTOP

    def on_command(self, event):
        if event[2] == 589824: #TBD use a constant name
            self.on_change()

    def set_value(self, value):
        self._send_message(defs.CB_SELECTSTRING, -1, unicode(value)) # CB_SETCURSEL, value, 0)

    def add_item(self, text):
        self._send_message(defs.CB_ADDSTRING, 0, unicode(text))

    def clear(self):
        self._send_message(defs.CB_RESETCONTENT, 0, 0)

    def on_change(self):
        pass

class SortedComboBox(ComboBox):
    _window_style_ = ComboBox._window_style_ | defs.CBS_SORT

class Button(Widget):
    _window_class_name_ = "BUTTON"
    _window_style_ = Widget._window_style_ | defs.BS_PUSHBUTTON | defs.WS_TABSTOP
    #~ _is_transparent_ = True
    #~ _window_ex_style_ = WS_EX_TRANSPARENT

    def on_command(self, event):
        if event[2] == 0:
            self.on_click()

    def is_checked(self):
        value = self._send_message(defs.BM_GETCHECK, 0, 0)
        return value == defs.BST_CHECKED

    def set_check(self, value):
        if value:
            value = defs.BST_CHECKED
        else:
            value = defs.BST_UNCHECKED
        self._send_message(defs.BM_SETCHECK, value, 0)

    def on_click(self):
        pass

class FlatButton(Button):
    _window_style_ = Widget._window_style_ | defs.BS_FLAT | defs.WS_TABSTOP

class DefaultButton(Button):
    _window_style_ = Widget._window_style_ | defs.BS_DEFPUSHBUTTON  | defs.WS_TABSTOP

class RadioButton(Button):
    _window_class_name_ = "BUTTON"
    _window_style_ = Widget._window_style_ | defs.BS_AUTORADIOBUTTON | defs.WS_TABSTOP
    _is_transparent_ = True

class GroupBox(Button):
    _window_class_name_ = "BUTTON"
    _window_style_ = Widget._window_style_ | defs.BS_GROUPBOX  #| WS_TABSTOP
    _is_transparent_ = True
    _window_ex_style_ = defs.WS_EX_CONTROLPARENT

class CheckButton(Button):
    _window_class_name_ = "BUTTON"
    _window_style_ = Widget._window_style_ | defs.BS_AUTOCHECKBOX  | defs.WS_TABSTOP
    _is_transparent_ = True

class Label(StaticWidget):
    _window_class_name_ = "Static"
    _window_style_ = StaticWidget._window_style_ | defs.SS_NOPREFIX

class Bitmap(StaticWidget):
    _window_class_name_ = "Static"
    _window_style_ = StaticWidget._window_style_ | defs.SS_BITMAP
    _window_ex_style_ = defs.WS_EX_TRANSPARENT

    def set_image(self, path, width=0, height=0):
        himage = ctypes.wintypes.windll.user32.LoadImageW(defs.NULL, path, defs.IMAGE_BITMAP, width, height, defs.LR_LOADFROMFILE);
        self._gdi_disposables.append(himage)
        self._send_message(defs.STM_SETIMAGE, defs.IMAGE_BITMAP, himage)

class Icon(StaticWidget):
    _window_class_name_ = "Static"
    _window_style_ = StaticWidget._window_style_|defs.SS_ICON

    def set_image(self, path, width=0, height=0):
        himage = ctypes.wintypes.windll.user32.LoadImageW(defs.NULL, path, defs.IMAGE_ICON, width, height, defs.LR_LOADFROMFILE);
        self._gdi_disposables.append(himage)
        self._send_message(defs.STM_SETIMAGE, defs.IMAGE_ICON, himage)

class ProgressBar(Widget):
    _window_class_name_ = "msctls_progress32"

    def set_position(self, position):
        return self._send_message(defs.PBM_SETPOS, position, 0)

    def get_position(self):
        return self._send_message(defs.PBM_GETPOS, 0, 0)

    def set_bar_color(self, color):
        return self._send_message(defs.PBM_SETBARCOLOR, 0, color)

    def set_background_color(self, clrBk):
        return self._send_message(defs.PBM_SETBKCOLOR, 0, clrBk)

    def step(self, n=1):
        step0 = self.get_position()
        #~ if not n:
            #~ step1 = self._send_message(PBM_STEPIT, 0, 0) #PBM_DELTAPOS
        step1 = self.set_position(step0 + n)
        self.on_change()
        return step1

    def on_change(self):
        pass

class Link(Widget):
    _window_class_name_ = "Link"

class Page(Window):
    _window_class_name_ = None
    _window_style_ = defs.WS_CHILD
    _window_ex_style_ = defs.WS_EX_CONTROLPARENT
