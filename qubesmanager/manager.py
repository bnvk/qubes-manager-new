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
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
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
		for q in qvm_collection.values():
			if q["icon"] != "default":
				image = q["icon"]
			else:
				image = "qube-32"
			pixbuf = Pixbuf.new_from_file("icons/" + image + ".png")

			qube = [q["type"], q["desc"], q["name"], pixbuf,
				q["get_power_state"], q["is_fully_usable"],
				q["is_guid_running"], q["is_networked"]
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
		self.vbox.pack_end(builder.get_object("footerBar"), False, False, 0)

		# Show All
		self.add(self.vbox)
		self.show_all()

	def create_qube_grid(self):
		"""Renders filterable IconView in a grid of qubes"""
		grid = Gtk.Grid()
		grid.set_column_homogeneous(True)
		grid.set_row_homogeneous(True)

		# Create Scrollable
		scrollable = Gtk.ScrolledWindow()
		scrollable.set_vexpand(True)

		# IconView
		iconview = Gtk.IconView.new()
		iconview.set_model(self.type_filter)
		iconview.set_columns(5)
		iconview.set_margin(10)
		iconview.set_item_padding(15)
		
		# Choose Icon & Text value in list
		iconview.set_pixbuf_column(3)
		iconview.set_text_column(1)

		# Attach iconview
		scrollable.add(iconview)
		grid.attach(scrollable, 0, 0, 8, 10)

		# connect to the "item-activated" signal
		iconview.connect('item-activated',
			self.on_qube_item_activated,
			self.type_filter)

		iconview.grab_focus()

		# Show "app" qubes by default
		self.type_filter.refilter()
		self.vbox.pack_start(grid, True, True, 0)

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

	def on_qube_item_activated(self, icon_view, tree_path, store_item):
		print "Grid button clicked: " + str(tree_path)

		self.type_filter[tree_path]

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

class QubesManager(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self)

	def do_activate(self):
		win = ManagerWindow(self)
		win.show_all()

	def do_startup(self):
		Gtk.Application.do_startup(self)

app = QubesManager()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
