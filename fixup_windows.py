# vim: set ts=4 sw=0 noet:
import gi
from gi.repository import Gdk, Gtk, cairo

import ctypes
gdk = ctypes.CDLL('libgdk-3-0.dll')
gdk.gdk_init()

####################
# Code to convert a C pointer to a PyGObject
# http://stackoverflow.com/questions/8668333/create-python-object-from-memory-address-using-gi-repository
# Refactored to use Capsule instead of CObject
class _PyGObject_Functions(ctypes.Structure):
	_fields_ = [
		('register_class',
			ctypes.PYFUNCTYPE(ctypes.c_void_p, ctypes.c_char_p,
				ctypes.c_int, ctypes.py_object, ctypes.py_object)),
		('register_wrapper',
			ctypes.PYFUNCTYPE(ctypes.c_void_p, ctypes.py_object)),
		('lookup_class',
			ctypes.PYFUNCTYPE(ctypes.py_object, ctypes.c_int)),
		('newgobj',
			ctypes.PYFUNCTYPE(ctypes.py_object, ctypes.c_void_p)),
		]

class PyGObjectCAPI(object):
	def __init__(self):
		self._as_void_ptr.restype = ctypes.c_void_p
		self._as_void_ptr.argtypes = [ctypes.py_object]
		addr = self._as_void_ptr(ctypes.py_object(
			gi._gobject._PyGObject_API))
		self._api = _PyGObject_Functions.from_address(addr)

	@staticmethod
	def _as_void_ptr(obj):
		name = ctypes.pythonapi.PyCapsule_GetName(obj)
		return ctypes.pythonapi.PyCapsule_GetPointer(obj, name)

	def pygobject_new(self, addr):
		return self._api.newgobj(addr)

capi = PyGObjectCAPI()
####################

# gdk_win32_screen_get_active_window is unimplemented (returns NULL).
# So, we implement it using winapi call GetForegroundWindow.
def get_active_window(screen):
	HWND = ctypes.windll.user32.GetForegroundWindow()
	if not HWND: return None
	display = gdk.gdk_display_get_default()
	winptr = gdk.gdk_win32_window_foreign_new_for_display(display, HWND)
	win = capi.pygobject_new(winptr)
	return win

# gdk_win32_screen_get_monitor_workarea is stubbed to use
# gdk_win32_screen_get_monitor_geometery. So, we implement it using winapi
# call GetMonitorInfo.
class RECT(ctypes.Structure):
	_fields_ = [('left', ctypes.c_long),
	            ('top', ctypes.c_long),
	            ('right', ctypes.c_long),
	            ('bottom', ctypes.c_long)]

class MONITORINFO(ctypes.Structure):
	_fields_ = [('cbSize', ctypes.c_ulong),
	            ('rcMonitor', RECT),
	            ('rcWork', RECT),
	            ('dwFlags', ctypes.c_ulong)]

	def __init__(self):
		ctypes.Structure.__init__(self)
		self.cbSize = ctypes.sizeof(MONITORINFO)

MONITOR_DEFAULTTONEAREST = 2
def get_monitor_workarea(screen, mon):
	# workaround gdk not saving the HMONITOR for a GdkWin32Monitor
	geom = screen.get_monitor_geometry(mon)
	rect = RECT(geom.x, geom.y, geom.x+geom.width, geom.y+geom.height)
	HMONITOR = ctypes.windll.user32.MonitorFromRect(ctypes.addressof(rect),
			MONITOR_DEFAULTTONEAREST)

	info = MONITORINFO()
	ctypes.windll.user32.GetMonitorInfoW(HMONITOR, ctypes.addressof(info))
	wa = info.rcWork
	rect = cairo.RectangleInt()
	rect.x, rect.y = wa.left, wa.top
	rect.width, rect.height = wa.right-wa.left, wa.bottom-wa.top
	return rect

# gdk_win32_window_set_accept_foucus(win, false) doesn't seem to work.
# So, we reimplement using winapi SetWindowLong with WS_EX_NOACTIVATE.
# Note that usually we'd also have to use WS_EX_APPWINDOW to make it appear
# in the taskbar, but we don't want that anyway.
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
SW_HIDE = 0
SW_SHOWNOACTIVATE = 4
old_set_accept_focus = Gtk.Window.set_accept_focus
def set_accept_focus(win, accept):
	old_set_accept_focus(win, accept)
	if not accept:
		HWND = gdk.gdk_win32_window_get_handle(hash(win.get_window()))
		if not HWND: return
		ctypes.windll.user32.ShowWindow(HWND, SW_HIDE)
		style = ctypes.windll.user32.GetWindowLongW(HWND, GWL_EXSTYLE)
		ctypes.windll.user32.SetWindowLongW(HWND, GWL_EXSTYLE, style | WS_EX_NOACTIVATE)
		ctypes.windll.user32.ShowWindow(HWND, SW_SHOWNOACTIVATE)

# Monkey patch to our fixed functions
Gdk.Screen.get_active_window = get_active_window
Gdk.Screen.get_monitor_workarea = get_monitor_workarea
Gtk.Window.set_accept_focus = set_accept_focus
