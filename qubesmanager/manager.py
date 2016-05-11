#!/usr/bin/python2
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2016 Brennan Novak <bnvk@invisiblethingslab.com>

import sys
import os
import os.path
import signal
import subprocess
import time
from datetime import datetime, timedelta

# Gtk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio
from gi.repository.GdkPixbuf import Pixbuf


# Qubes Test Data
import tests.data_vmcollection
qvm_collection = tests.data_vmcollection


class GenericDialog(Gtk.Dialog):

	def __init__(self, parent):

		Gtk.Dialog.__init__(self, "Search", parent,
			Gtk.DialogFlags.MODAL, buttons=(
			Gtk.STOCK_FIND, Gtk.ResponseType.OK,
			Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

		box = self.get_content_area()

		label = Gtk.Label("Insert text you want to search for:")
		box.add(label)

		self.entry = Gtk.Entry()
		box.add(self.entry)

		self.show_all()


class ManagerWindow(Gtk.ApplicationWindow):

	def __init__(self, app):

		# Setup Window
		Gtk.Window.__init__(self, title="Qubes Manager", application=app)
		self.set_default_size(800, 600)
		self.set_resizable(True)
		self.set_position(Gtk.WindowPosition.CENTER)

		# Load Glade UI
		builder = Gtk.Builder()
		try:
			builder.add_from_file("glade/manager.glade")
		except:
			print("file not found")
			sys.exit()

		builder.connect_signals(self)

		# Elements
		self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.vbox.pack_start(builder.get_object("menubarMain"), False, False, 0)

		# Toolbar
		self.vbox.pack_start(builder.get_object("toolbarMain"), False, False, 0)
		self.vbox.pack_start(Gtk.Separator(), False, False, 0)

		#builder.get_object("toolbuttonHelp")

		#menu = Gio.Menu()
		#menu.append("Browse Files", "app.device_browse")
		#menu.append("Eject Device", "app.device_eject")
		#button.set_menu_model(menu)


		# Header of qube
		headerApps = builder.get_object("headerApps")
		headerNetworking = builder.get_object("headerNetworking")
		headerTemplates = builder.get_object("headerTemplates")

		self.qubes_header = {
			"app": headerApps,
			"net": headerNetworking,
			"template": headerTemplates
		}

		self.vbox.pack_start(self.qubes_header["app"], False, False, 0)
		self.vbox.pack_start(Gtk.Separator(), False, False, 0)

		# ListStore of qubes
		self.qubes_liststore = Gtk.ListStore(str, str, str, Pixbuf, str,
											 bool, bool, bool)
		for qube in qvm_collection.values():
			if qube["icon"] != "default":
				image = qube["icon"]
			else:
				image = "qube-32"
			pixbuf = Pixbuf.new_from_file("icons/" + image + ".png")

			qube = [qube["type"], qube["desc"], qube["name"], pixbuf,
				qube["get_power_state"], qube["is_fully_usable"],
				qube["is_guid_running"], qube["is_networked"]
			]

			self.qubes_liststore.append(qube)

		# Filter Values
		self.current_filter 		= "All"
		self.current_filter_type 	= "app"
		self.current_filter_state 	= "All"

		self.filter_states = ["All", "Running", "Halted", "Networked"]

		# Create filter
		self.type_filter = self.qubes_liststore.filter_new()
		self.type_filter.set_visible_func(self.type_filter_func)

		# Main Grid of qubes
		self.create_qube_grid()

		# Bottom Footer
		self.vbox.pack_start(Gtk.Separator(), False, False, 0)

		footerBox = Gtk.Box(spacing=10)
		footerBox.set_border_width(10)	

		# Add System qubes
		for qube in qvm_collection.values():
			if qube["type"] == "sys":
				sys_button = self.create_sys_qube_button(qube)
				footerBox.pack_start(sys_button, False, False, 0)

		footerSeparator = Gtk.Separator(orientation="vertical")
		footerSeparator.set_margin_left(10)
		footerSeparator.set_margin_right(10)
		footerBox.pack_start(footerSeparator, False, False, 0)

		# Add Devices
		for qube in qvm_collection.values():
			if qube["type"] == "dev":
				device_button = self.create_device_button(qube)
				footerBox.pack_start(device_button, False, False, 0)

		footerBox.pack_end(builder.get_object("systemButtons"), False, False, 0)
		self.vbox.pack_end(footerBox, False, False, 0)

		# Show All
		self.add(self.vbox)
		self.show_all()

	def create_qube_grid(self):
		"""Renders filterable IconView in a grid of qubes"""
		grid = Gtk.Grid()
		grid.set_column_homogeneous(True)
		grid.set_row_homogeneous(True)

		# Create Scrollable
		scrolled = Gtk.ScrolledWindow()
		scrolled.set_vexpand(True)

		# Receive signals from mouse clicks in IconView
		Gtk.IconView.add_events(self, Gdk.EventMask.BUTTON_PRESS_MASK)

		# IconView of qubes
		iconview = Gtk.IconView.new()
		iconview.set_model(self.type_filter)
		iconview.set_columns(5)
		iconview.set_margin(10)
		iconview.set_item_padding(15)

		# Choose Icon & Text value in list
		iconview.set_pixbuf_column(3)
		iconview.set_text_column(1)

		# Attach iconview
		scrolled.add(iconview)
		grid.attach(scrolled, 0, 0, 8, 10)

		# Make IconView items clickable w/ "item-activated"
		# iconview.connect('activate-on-single-click',
		iconview.connect('item-activated',
			self.on_qube_item_double_click,
			self.type_filter)

		# Single Click
		iconview.connect('button-press-event',
			self.on_qube_item_single_click)

		# Focus and show "app" qubes
		iconview.grab_focus()
		self.type_filter.refilter()
		self.vbox.pack_start(grid, True, True, 0)

	def create_sys_qube_button(self, qube):
		"""Creates button for system qube"""
		menu = Gio.Menu()

		# Add state/status items
		if (qube["is_guid_running"] == True and
			qube["get_power_state"] == "Running"):

			# Add "restart" if needed
			if qube["is_outdated"] == True or qube["is_fully_usable"] == False:
				menu.append("Restart (pending updates)", "app.qube_restart")

			# Add "shutdown" always
			menu.append("Shutdown", "app.qube_shutdown")
		else:
			menu.append("Start", "app.qube_start")

		# TODO: specials actions by device type
		# - app -> launch applications
		# - networking -> create proxy
		# - system -> browse files, drivers?

		# Menu always items
		menu.append("Backups", "app.qube_backups")
		menu.append("Options", "app.qube_overview")

		# TODO: determine icon by sys type (wifi, usb, sd, bluetooth)
		# TODO: determine modify icon by state (running, halted, updateable)
		if qube["icon"] != "default":
			image = qube["icon"]
		else:
			image = "qube-32"

		icon = Gtk.Image.new_from_file("icons/" + image + ".png")
		icon.set_margin_bottom(5)

		button = Gtk.MenuButton()
		button.set_label(qube["desc"])
		button.set_image_position(Gtk.PositionType.TOP)
		button.set_image(icon)
		button.set_relief(Gtk.ReliefStyle.NONE)
		button.set_size_request(70, 80)
		button.set_menu_model(menu)

		return button

	def create_device_button(self, device):
		"""Creates button & menu for attached device"""
		# TODO: determine icon by device type (thumbdrive, printer...)
		icon = Gtk.Image.new_from_file("icons/" + device["icon"] + ".png")
		icon.set_margin_bottom(5)
	
		button = Gtk.MenuButton()
		button.set_label(device["desc"])
		button.set_image_position(Gtk.PositionType.TOP)
		button.set_image(icon)
		button.set_relief(Gtk.ReliefStyle.NONE)
		button.set_size_request(70, 80)

		# Menu Actions
		# TODO: determine actions by device type (drive -> browse, printer...)
		menu = Gio.Menu()
		menu.append("Browse Files", "app.device_browse")
		menu.append("Eject Device", "app.device_eject")
		button.set_menu_model(menu)

		return button

	def replace_qube_header(self, old, new):
		parent = self.qubes_header[old].get_parent()
		props= {}
		for key in Gtk.ContainerClass.list_child_properties(type(parent)):
			props[key.name]= parent.child_get_property(self.qubes_header[old],
													   key.name)
		parent.remove(self.qubes_header[old])
		parent.add(self.qubes_header[new])
		self.qubes_header[new].show_all()

		for name, value in props.iteritems():
			parent.child_set_property(self.qubes_header[new], name, value)

	def type_filter_func(self, model, iter, data):
		"""Checks if row is the selected filters"""
		# Type or State
		if self.current_filter in ["app", "net", "sys", "templates"]:
			current_filter_is = "type"
		elif self.current_filter in ["All", "Running", "Halted", "Networked"]:
			current_filter_is = "network"
		else:
			current_filter_is = "error"

		# Show all
		if (self.current_filter_type == "All" and
			self.current_filter_state == "All"):
			return True
		# Filter by state
		elif self.current_filter_type == "All":
			return model[iter][4] == self.current_filter_state
		# Filter by state
		elif self.current_filter_state == "All":
			return model[iter][0] == self.current_filter_type
		# Filter by both
		else:
			chk_type = model[iter][0] == self.current_filter_type
			chk_state = model[iter][4] == self.current_filter_state
			if chk_type == True and chk_state == True:
				return True
			else:
				return False

	def on_clicked_qubes_logo(self, button):

		# AboutDialog
		about = Gtk.AboutDialog()
		about.set_position(Gtk.WindowPosition.CENTER)

		# Authors & Documenters
		# TODO: perhaps automate this / use full list on website?
		authors = ["Joanna Rutkowska", "Marek Marczykowski",
				   "Wojciech Porczyk", "Rafal Wojdyla", "Patrick Schleizer",
				   "Alexander Tereshkin", "Rafal Wojtczuk"]

		documenters = ["Andrew David Wong", "Hashiko Nukama", "Michael Carbone",
					   "Brennan Novak", "The Qubes OS Community"]

		logo = Pixbuf.new_from_file("icons/qubes-logo.png")

		# Add values
		about.set_logo(logo)
		about.set_program_name("Qubes Manager")
		about.set_copyright("Copyright \xc2\xa9 2016 Qubes OS")
		about.set_authors(authors)
		about.set_documenters(documenters)
		about.set_website("https://qubes-os.org")
		about.set_website_label("Qubes OS Website")

		# Connect close about response
		about.connect("response", self.on_clicked_close_about)

		# Show dialog
		about.show()

	def on_clicked_close_about(self, action, parameter):
		action.destroy()

	# Filter "qubes" events
	def on_state_combo_changed(self, combo):
		"""Event for header ComboBox to filter qubes by state"""
		self.current_filter_state = self.filter_states[combo.get_active()]
		self.current_filter = self.current_filter_state
		self.type_filter.refilter()

	def on_type_toggled(self, widget):
		"""Event for toolbar RadioButtons to filter qubes by type"""
		new_type = "app"
		if widget.get_active():
			# Determine type by active widget name value
			# hack to not change 'qube.type' value of test data
			if Gtk.Buildable.get_name(widget) == 'radioApplications':
				new_type = "app"
			if Gtk.Buildable.get_name(widget) == 'radioNetworking':
				new_type = "net"
			if Gtk.Buildable.get_name(widget) == 'radioTemplates':
				new_type = "template"

		self.replace_qube_header(self.current_filter_type, new_type)
		self.current_filter_type = new_type
		self.current_filter = self.current_filter_type
		self.type_filter.refilter()

	def on_clicked_dialog(self, widget, value):
		print "Load GenericDialogue for: " + value
		dialog = GenericDialog(self)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			cursor_mark = self.textbuffer.get_insert()
			start = self.textbuffer.get_iter_at_mark(cursor_mark)
			if start.get_offset() == self.textbuffer.get_char_count():
				start = self.textbuffer.get_start_iter()
			self.search_and_mark(dialog.entry.get_text(), start)
		dialog.destroy()

	def on_qube_item_double_click(self, icon_view, tree_path, store_item):
		print "Grid item double clicked (activated): " + str(tree_path)
		self.type_filter[tree_path]

	def on_qube_item_single_click(self, iconview, event):
		if event.button == 3:
			print "Grid item single clicked RIGHT"
		else:
			print "Grid item single clicked LEFT"


	# Toolbar Buttons
	def on_clicked_launch_recipes(self, button):
		print "launch Recipes"

	def on_clicked_launch_backups(self, button):
		print "launch Backups"

	def on_clicked_launch_help(self, button):
		print "launch Help"

	def on_clicked_launch_settings(self, button):
		print "launch Settings"

	# Header Applications
	def on_clicked_install_app_qube(self, button):
		print "install app qube"

	def on_clicked_attach_mic(self, button):
		print "install attach mic"

	def on_clicked_create_qube(self, button):
		print "install create qube"

	# Header Networking
	def on_clicked_captive_portal(self, button):
		print "launch captive portal"

	def on_clicked_stop_all_networking(self, button):
		print "stop all networking"

	def on_clicked_new_proxy(self, button):
		print "create new proxy"

	def in_clicked_new_device(self, button):
		print "create new networking device qube"

	# Header Templates
	def on_clicked_install_app_template(self, button):
		print "install app in template"

	def on_clicked_update_templates(self, button):
		print "update all templates"

	def on_clicked_new_template(self, button):
		print "find new templates"

	def on_clicked_clone_template(self, button):
		print "clone new template"

	# Sytem Items
	def on_clicked_system_files(self, button):
		print "launch system file browser"

	def on_clicked_system_terminal(self, button):
		print "launch system terminal"


class QubesManager(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self,
								 application_id="org.invisiblethingslab.qubes",
								 flags=Gio.ApplicationFlags.FLAGS_NONE)

	def do_activate(self):
		win = ManagerWindow(self)
		win.show_all()

	def do_startup(self):
		Gtk.Application.do_startup(self)

		# Actions for qubes
		action_qube_backups = Gio.SimpleAction.new("qube_backups", None)
		action_qube_backups.connect("activate", self.qube_backups_callback)
		self.add_action(action_qube_backups)
		
		action_qube_overview = Gio.SimpleAction.new("qube_overview", None)
		action_qube_overview.connect("activate", self.qube_overview_callback)
		self.add_action(action_qube_overview)

		action_qube_start = Gio.SimpleAction.new("qube_start", None)
		action_qube_start.connect("activate", self.qube_start_callback)
		self.add_action(action_qube_start)

		action_qube_shutdown = Gio.SimpleAction.new("qube_shutdown", None)
		action_qube_shutdown.connect("activate", self.qube_shutdown_callback)
		self.add_action(action_qube_shutdown)

		action_qube_restart = Gio.SimpleAction.new("qube_restart", None)
		action_qube_restart.connect("activate", self.qube_restart_callback)
		self.add_action(action_qube_restart)

		# Actions for attached devices
		action_device_browse = Gio.SimpleAction.new("device_browse", None)
		action_device_browse.connect("activate", self.device_browse_callback)
		self.add_action(action_device_browse)

		device_eject = Gio.SimpleAction.new("device_eject", None)
		device_eject.connect("activate", self.device_eject_callback)
		self.add_action(device_eject)

	# Callbacks for qubes
	def qube_backups_callback(self, action, parameter):
		print("clicked: show qube Backup")

	def qube_overview_callback(self, action, parameter):
		print("clicked: show qube Overview")

	def qube_start_callback(self, action, parameter):
		print("clicked: qube Start")
	
	def qube_shutdown_callback(self, action, parameter):
		print("clicked: qube Shutdown")

	def qube_restart_callback(self, action, parameter):
		print("clicked: qube Restart")

	# Callbacks for devices
	def device_browse_callback(self, action, parameter):
		print("clicked: Browse Device")

	def device_eject_callback(self, action, parameter):
		print("clicked: Eject Device")


app = QubesManager()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
