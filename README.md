Trellis
=======
Inspired by [Divvy](http://mizage.com/divvy/), [gTile](https://extensions.gnome.org/extension/28/gtile/), and [ration](https://github.com/onyxfish/ration), Trellis allows you to flexibly arrange windows on a configurable grid. 

Dependencies
---
- [Python 2.7+ or 3.1+](https://www.python.org/downloads/)
- [GTK+ 3.14+](http://www.gtk.org/)
- [PyGObject](http://sourceforge.net/projects/pygobjectwin32/files/)

Windows: Python and PyGObject

Debian-based distros: python-gi or python3-gi

Fedora-based distros: pygobject2 or pygobject3

Gentoo-based distros: pygobject

Use
---
Run trellis.py . Trellis will create a tray icon and show its windows, one per monitor. Trellis's windows can be used to resize the focused window according to Trellis's grid.

You can hide Trellis's windows by closing one; clicking on the tray icon will toggle Trellis's shown/hidden state. Re-running trellis.py will also show Trellis's windows; a second Trellis process will not be created.

To quit Trellis, right-click the tray icon, and select Quit.

Trellis can be configured by editing the CONFIG dictionary near the top of trellis.py . Trellis will need to be restarted after changing the configuration. Configuration variables:
- rows: the height of the Trellis grid.
- columns: the width of the Trellis grid.
- autohide:
  - if True, hide Trellis's windows after resizing a window with it.
  - if False, leave Trellis's windows shown after resizing a window with it.

TODO
---
- handle resize cancellation (~~release drag off window~~ or press esc)
- ~~handle multi-monitor~~ Done? Test more.
- ~~complete Windows support~~ Done? Test more.
- handle multi-workspace / multi-desktop (see possibly gdk_x11_screen_get_number_of_desktops, gdk_x11_screen_get_current_desktop, gdk_x11_window_move_to_(current_)desktop)
- correctly resize client-side decorated windows with shadows (missing Gdk.Window.get_shadow_width(), GNOME Software or Files are good tests)
- show window name? (missing Gdk.Window.get_title())
- implement prefs/config storage, UI
- global hotkey(s)
- esc to close window
- check OSX
- [Slim PyGI installer](http://ascend4.org/Creating_slim_PyGI_installer_for_Windows)
