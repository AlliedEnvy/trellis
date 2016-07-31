#! /usr/bin/env python
# vim: set ts=4 sw=0 noet:
from __future__ import absolute_import, division, print_function, unicode_literals
from gi.repository import Gdk, Gtk, Gio
import sys

if sys.platform.startswith('win'):
	import fixup_windows

CONFIG = {
	'rows': 6,
	'columns': 12,
	'autohide': False
}

class TrellisButton(Gtk.ToggleButton):
	def __init__(self):
		Gtk.ToggleButton.__init__(self)
		#self.set_relief(Gtk.ReliefStyle.NONE)
		self.set_hexpand(True)
		self.set_vexpand(True)

class TrellisWindow(Gtk.Window):
	def __init__(self, monitor):
		Gtk.Window.__init__(self, title='Trellis')

		self.monitor = monitor
		rect = Gdk.Screen.get_default().get_monitor_workarea(self.monitor)

		self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
		#self.set_position(Gtk.WindowPosition.CENTER_ALWAYS) #doesn't handle multi-monitor?
		self.set_resizable(False)
		self.set_keep_above(True)
		self.stick()
		#TODO: do these do anything?
		#self.set_skip_pager_hint(True)
		#self.set_skip_taskbar_hint(True)

		self.grid = Gtk.Grid()
		self.grid.set_size_request(rect.width * 0.2, rect.height * 0.2)
		#self.grid.set_row_spacing(4)
		#self.grid.set_column_spacing(4)

		self.gesture = Gtk.GestureDrag.new(self.grid)
		self.gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
		self.gesture.set_button(1)
		self.gesture.connect('drag-update', self.drag_update_handler)
		self.gesture.connect('drag-end', self.drag_end_handler)

		self.add(self.grid)

		self.preview = Gtk.Window()
		self.preview.set_name('preview')
		self.preview.set_type_hint(Gdk.WindowTypeHint.UTILITY)
		self.preview.set_decorated(False)
		#self.preview.set_resizable(False)
		self.preview.set_keep_above(True)
		self.preview.stick()
		self.preview.show_all()
		self.preview.set_accept_focus(False)
		self.preview.set_opacity(0.4)
		self.preview.hide()

		self.connect('leave-notify-event', self.preview_hide)

		for y in range(CONFIG['rows']):
			for x in range(CONFIG['columns']):
				b = TrellisButton()
				self.grid.attach(b, x, y, 1, 1)
				b.connect('enter-notify-event', self.preview_show, x, y)

		self.connect('delete-event', self.delete_handler)
		self.show_all()
		self.set_accept_focus(False)
		self.set_opacity(0.8)

	def delete_handler(self, *args):
		self.get_application().dismiss()
		return True

	def engage(self, *args):
		rect = Gdk.Screen.get_default().get_monitor_workarea(self.monitor)
		self.show()
		self.grid.set_size_request(rect.width * 0.2, rect.height * 0.2)
		frame = self.get_window().get_frame_extents()
		self.move((rect.width-frame.width)/2+rect.x, (rect.height-frame.height)/2+rect.y)

	def dismiss(self, *args):
		self.gesture.emit("cancel", None)
		
		self.preview.hide()
		self.hide()

	def point_to_grid(self, x, y):
		w = self.grid.get_allocated_width()
		h = self.grid.get_allocated_height()
		if x < 0 or y < 0 or x >= w or y >= h:
			return None
		return ((x*CONFIG['columns'])//w, (y*CONFIG['rows'])//h)

	def drag_end_handler(self, gesture, offset_x, offset_y):
		start = gesture.get_start_point()
		pt = self.point_to_grid(offset_x + start[1], offset_y + start[2])
		start = self.point_to_grid(start[1], start[2])
		if pt:
			min_x, min_y = min(start[0], pt[0]), min(start[1], pt[1])
			max_x, max_y = max(start[0], pt[0]), max(start[1], pt[1])

			rect = Gdk.Screen.get_default().get_monitor_workarea(self.monitor)
			win = Gdk.Screen.get_default().get_active_window().get_effective_toplevel()

			if min_x == 0 and min_y == 0 and max_x+1 == CONFIG['columns'] and max_y+1 == CONFIG['rows']:
				prev_monitor = Gdk.Screen.get_default().get_monitor_at_window(win)
				if  prev_monitor != self.monitor:
					# Unfortunately, we can't maximize to another monitor.
					# So, we move the window to hopefully the least surprising
					# position on the other monitor, before maximizing.
					prev_rect = Gdk.Screen.get_default().get_monitor_workarea(prev_monitor)
					win.unmaximize()
					prev_frame = win.get_frame_extents()
					x = round(prev_frame.x/prev_rect.width*rect.width)
					y = round(prev_frame.y/prev_rect.height*rect.height)
					
					x = min(x, rect.width - prev_frame.width)
					y = min(y, rect.height - prev_frame.height)

					x += rect.x
					y += rect.y
					
					win.move(x, y)
				win.maximize()
			else:
				ux = rect.width / CONFIG['columns']
				uy = rect.height / CONFIG['rows']

				win.unmaximize()
				frame = win.get_frame_extents()
				geom = win.get_geometry()

				x = round(ux*min_x + rect.x)
				y = round(uy*min_y + rect.y)
				w = round(ux*(max_x-min_x+1)) + geom[2]-frame.width
				h = round(uy*(max_y-min_y+1)) + geom[3]-frame.height

				win.move_resize(x, y, w, h)

			if CONFIG['autohide']: self.delete_handler()

		for y in range(CONFIG['rows']):
			for x in range(CONFIG['columns']):
				self.grid.get_child_at(x, y).set_active(False)
				self.grid.get_child_at(x, y).released()

		self.preview.hide()

	def drag_update_handler(self, gesture, offset_x, offset_y):
		start = gesture.get_start_point()
		pt = self.point_to_grid(offset_x + start[1], offset_y + start[2])
		start = self.point_to_grid(start[1], start[2])
		if not pt:
			self.preview.hide()
		else:
			self.preview_show(None, None, pt[0], pt[1])

			min_x, min_y = min(start[0], pt[0]), min(start[1], pt[1])
			max_x, max_y = max(start[0], pt[0]), max(start[1], pt[1])

			for y in range(CONFIG['rows']):
				for x in range(CONFIG['columns']):
					b = self.grid.get_child_at(x, y)
					if x >= min_x and x <= max_x and y >= min_y and y <= max_y:
						if not b.get_active():
							b.set_active(True)
					elif b.get_active():
						b.set_active(False)
	
	def preview_show(self, widget, event, bx, by):
		rect = Gdk.Screen.get_default().get_monitor_workarea(self.monitor)
		ux = rect.width / CONFIG['columns']
		uy = rect.height / CONFIG['rows']

		if self.gesture.is_active():
			start = self.gesture.get_start_point()
			offset = self.gesture.get_offset()
			pt = self.point_to_grid(start[1] + offset[1], start[2] + offset[2])
			start = self.point_to_grid(start[1], start[2])
			min_x, min_y = min(start[0], pt[0]), min(start[1], pt[1])
			max_x, max_y = max(start[0], pt[0]), max(start[1], pt[1])
		else:
			min_x, min_y = bx, by
			max_x, max_y = bx, by

		x = round(ux*min_x + rect.x)
		y = round(uy*min_y + rect.y)
		w = round(ux*(max_x-min_x+1))
		h = round(uy*(max_y-min_y+1))

		self.preview.show()
		self.preview.get_window().move_resize(x, y, w, h)
		self.present() #this is a hack to keep preview below dialog
		return True
	
	def preview_hide(self, widget, event):
		self.preview.hide()
		return True

class TrellisApp(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self,
		                         application_id='com.alliedenvy.trellis',
		                         flags=Gio.ApplicationFlags.FLAGS_NONE,
		                         register_session=True)

		self.connect('activate', self.engage)
		self.connect('startup', self.signal_startup)
		self.connect('shutdown', self.signal_shutdown)
	
	def signal_startup(self, data=None):
		self.hold()

		css = b'''
			#preview {
				background-color: rgb(0%, 80%, 100%);
				border-width: 4px;
				border-style: solid;
				border-color: #ACF;
			}
		'''

		style_provider = Gtk.CssProvider()
		style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),
				style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		self.engaged = True

		self.status_icon = Gtk.StatusIcon.new_from_icon_name('zoom-fit-best')
		self.status_icon.set_name('Trellis')
		self.status_icon.set_title('Trellis')
		self.status_icon.set_tooltip_text('Trellis')
		self.status_icon.set_visible(True)

		self.menu = Gtk.Menu()
		quit_item = Gtk.MenuItem.new_with_mnemonic('_Quit')
		quit_item.connect('activate', self.signal_shutdown)
		self.menu.append(quit_item)
		self.menu.show_all()

		self.status_icon.connect('activate', self.status_activate)
		self.status_icon.connect('popup-menu', self.status_popup_menu)

		self.windows = []
		self.redo_monitors(Gdk.Screen.get_default())
		Gdk.Screen.get_default().connect('size-changed', self.redo_monitors)
		#Gdk.Screen.get_default().connect('monitors-changed', self.redo_monitors)

	def signal_shutdown(self, data=None):
		self.quit()

	def status_activate(self, *args):
		self.toggle()
	
	def status_popup_menu(self, status_icon, button, time):
		self.menu.popup(None, None, None, None, button, time)

	def engage(self, *args):
		for win in self.windows:
			win.engage()
		self.engaged = True

	def dismiss(self, *args):
		for win in self.windows:
			win.dismiss()
		self.engaged = False
	
	def toggle(self, *args):
		if self.engaged:
			self.dismiss()
		else:
			self.engage()
	
	def redo_monitors(self, screen):
		while len(self.windows) < screen.get_n_monitors():
			self.windows.append(TrellisWindow(len(self.windows)))
			self.add_window(self.windows[-1])
			if self.engaged:
				self.windows[-1].engage()
		while len(self.windows) > screen.get_n_monitors():
			self.remove_window(self.windows[-1])
			self.windows.pop().destroy()

if __name__ == '__main__':
	app = TrellisApp()
	app.run(sys.argv)
