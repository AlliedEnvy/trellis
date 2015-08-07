Trellis
=======
Inspired by [Divvy](http://mizage.com/divvy/), [gTile](https://extensions.gnome.org/extension/28/gtile/), and [ration](https://github.com/onyxfish/ration), Trellis allows you to flexibly arrange windows on a configurable grid. 

Dependencies
---
- [Python 2.7+ or 3+](https://www.python.org/downloads/)
- [GTK+ 3.10+](http://www.gtk.org/)
- [PyGObject](http://sourceforge.net/projects/pygobjectwin32/files/)

Windows: Python and PyGObject

Debian-based distros: python-gi or python3-gi

Fedora-based distros: pygobject2 or pygobject3

Gentoo-based distros: pygobject

TODO
---
- handle resize cancellation (release drag off window or press esc)
- ~~handle multi-monitor~~ Done? Test more.
- ~~complete Windows support~~ Done? Test more.
- handle multi-workspace / multi-desktop (see possibly gdk_x11_screen_get_number_of_desktops, gdk_x11_screen_get_current_desktop, gdk_x11_window_move_to_(current_)desktop)
- correctly resize client-side decorated windows with shadows (missing Gdk.Window.get_shadow_width(), GNOME Software or Files are good tests)
- show window name? (missing Gdk.Window.get_title())
- implement prefs/config storage, UI
- [Slim PyGI installer](http://ascend4.org/Creating_slim_PyGI_installer_for_Windows)
