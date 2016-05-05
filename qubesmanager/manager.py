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

# Manager
from qubesmanager.handler import *

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

		# Elements
		menubarMain = builder.get_object("menubarMain")

		# Main Vertical Box
		self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.vbox.pack_start(menubarMain, False, False, 0)

		# Toolbar
		self.create_toolbar()
		self.vbox.pack_start(Gtk.Separator(), False, False, 0)

		# Header of qube
		self.qubes_header = {
			"app": self.create_app_header(),
			"net": self.create_net_header(),
			"template": self.create_template_header()
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
		# self.create_qube_list()
		self.create_qube_grid()

		# Bottom Footer
		self.vbox.pack_start(Gtk.Separator(), False, False, 0)
		self.create_footer()

		self.add(self.vbox)
		self.show_all()


	def create_toolbar(self):
		"""Creates main top toolbar"""
		toolbar = Gtk.Toolbar()
		toolbar.set_icon_size(Gtk.IconSize.DND)

		# Qube "type" radio buttons
		button_logo = Gtk.ToolButton()
		button_logo_image = Gtk.Image()
		button_logo_image.set_from_file("icons/qubes-logo-name.png")
		button_logo_image.set_margin_left(5)
		button_logo_image.set_margin_right(5)
		button_logo.set_icon_widget(button_logo_image)
		button_logo.set_margin_left(10)
		button_logo.set_margin_right(10)

		toolbar.insert(button_logo, 0)
		toolbar_separator1 = Gtk.SeparatorToolItem()
		toolbar.insert(toolbar_separator1, 1)

		apps = self.radio_button("Applications", "applications-office", False)
		apps.connect("toggled", self.on_type_toggled, "app")

		net = self.radio_button("Networking", "network-transmit-receive", apps)
		net.connect("toggled", self.on_type_toggled, "net")

		templates = self.radio_button("Templates", "package-x-generic", apps)
		templates.connect("toggled", self.on_type_toggled, "template")

		toolbar.insert(apps, 2)
		toolbar.insert(net, 3)
		toolbar.insert(templates, 4)
		toolbar_separator2 = Gtk.SeparatorToolItem()
		toolbar_separator2.set_margin_left(10)
		toolbar.insert(toolbar_separator2, 5)

		# Other buttons
		search = self.tool_button("Recipes", "applications-science")
		search.connect("clicked", self.on_clicked_dialog)
	
		backups = self.tool_button("Backups", "emblem-downloads")
		backups.connect("clicked", self.on_clicked_dialog, "Backups")

		docs = self.tool_button("Help", "help-browser")
		docs.connect("clicked", self.on_clicked_dialog, "Help")

		settings = self.tool_button("Settings", "applications-system")
		settings.connect("clicked", self.on_clicked_dialog, "Settings")

		toolbar.insert(search, 6)
		toolbar.insert(backups, 7)
		toolbar.insert(docs, 8)
		toolbar.insert(settings, 9)
		toolbar.show_all()

		# Add to main Box
		self.vbox.pack_start(toolbar, False, False, 0)

	def radio_button(self, label, icon, from_widget):
		"""Renders RadioToolButton with label and icon """
		if from_widget:
			radio = Gtk.RadioToolButton.new_from_widget(from_widget)
		else:
			radio = Gtk.RadioToolButton()

		radio_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		
		image = Gtk.Image()
		image.set_from_icon_name(icon, Gtk.IconSize.DND)
		image.set_margin_top(10)
		image.set_margin_bottom(5)
		radio_box.pack_start(image, False, False, 0)

		text = Gtk.Label()
		text.set_label(label)
		radio_box.pack_start(text, False, False, 0)

		radio.set_icon_widget(radio_box)
		radio.set_margin_left(10)
		radio.show()

		return radio

	def tool_button(self, label, icon):
		"""Renders ToolButton with label, icon, and event"""
		button = Gtk.ToolButton()
		#button_box = Gtk.Box()
		button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

		image = Gtk.Image()
		image.set_from_icon_name(icon, Gtk.IconSize.DND)
		image.set_margin_top(10)
		image.set_margin_bottom(5)
		button_box.pack_start(image, False, False, 0)

		text = Gtk.Label()
		text.set_label(label)
		button_box.pack_start(text, False, False, 0)

		button.set_icon_widget(button_box)
		button.set_margin_left(10)
		button.show()

		return button

	def create_app_header(self):
		header = Gtk.Box(spacing=15)
		header.set_border_width(10)

		install = self.icon_button("Install Apps", "application-x-executable")
		install.connect("clicked", self.on_button_clicked, "Install Apps")
		header.pack_start(install, True, True, 0)

		microphone = self.icon_button("Attach Microphone", "audio-input-microphone")
		microphone.connect("clicked", self.on_button_clicked, "Attach Mic")
		header.pack_start(microphone, True, True, 0)

		create_qube = self.icon_button("Create Qube", "list-add")
		create_qube.connect("clicked", self.on_button_clicked, "Create Qube")
		header.pack_start(create_qube, True, True, 0)

		filter_states = ["All", "Running", "Halted", "Networked"]
		state_combo = Gtk.ComboBoxText()
		state_combo.set_entry_text_column(0)
		state_combo.connect("changed", self.on_state_combo_changed)
		for state in filter_states:
			state_combo.append_text(state)
		header.pack_start(state_combo, True, True, 0)

		return header

	def create_net_header(self):
		header = Gtk.Box(spacing=15)
		header.set_border_width(10)

		captive = self.icon_button("Captive Portal", "dialog-password")
		captive.connect("clicked", self.on_button_clicked, "Captive Portal")
		header.pack_start(captive, True, True, 0)

		stop_all = self.icon_button("Stop All", "dialog-error")
		stop_all.connect("clicked", self.on_button_clicked, "Stop All")
		header.pack_start(stop_all, True, True, 0)

		new_device = self.icon_button("New Device", "network-wireless")
		new_device.connect("clicked", self.on_button_clicked, "New Device")
		header.pack_start(new_device, True, True, 0)

		new_proxy = self.icon_button("New Proxy", "network-server")
		new_proxy.connect("clicked", self.on_button_clicked, "New Proxy")
		header.pack_start(new_proxy, True, True, 0)

		return header	

	def create_template_header(self):
		header = Gtk.Box(spacing=15)
		header.set_border_width(10)

		install = self.icon_button("Install Apps", "application-x-executable")
		install.connect("clicked", self.on_button_clicked, "Install Apps")
		header.pack_start(install, True, True, 0)

		update = self.icon_button("Update Templates", "system-software-update")
		update.connect("clicked", self.on_button_clicked, "Update Templates")
		header.pack_start(update, True, True, 0)

		new_temp = self.icon_button("New Template", "window-new")
		new_temp.connect("clicked", self.on_button_clicked, "New Template")
		header.pack_start(new_temp, True, True, 0)

		clone_temp = self.icon_button("Clone Template", "document-save-as")
		clone_temp.connect("clicked", self.on_button_clicked, "Clone Template")
		header.pack_start(clone_temp, True, True, 0)

		return header

	def icon_button(self, label, icon):
		"""Renders button of qube that shows overview"""
		button = Gtk.Button()
		button.set_label(label)
		image = Gtk.Image()

		image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)
		image.show()
		image.set_margin_right(10)
		
		button.set_label(label)
		button.set_image_position(Gtk.PositionType.LEFT)
		button.set_image(image)

		return button

	def create_qube_list(self):

		# Set up grid in which the elements are
		grid = Gtk.Grid()
		grid.set_column_homogeneous(True)
		grid.set_row_homogeneous(True)

		# Create treeview, filter as a model, add columns
		treeview = Gtk.TreeView.new_with_model(self.type_filter)
		for i, column_title in enumerate([
				"Type", "Icon", "Name", "Desc", "Power State", "Usable",
				"Running", "Networked"
			]):
			renderer = Gtk.CellRendererText()
			renderer.set_fixed_size(100, 20)
			renderer.set_padding(5, 5)

			column = Gtk.TreeViewColumn(column_title, renderer, text=i)
			column.set_fixed_width(100)			

			treeview.append_column(column)

		# Create layout, vertical expand (?), attach treelist
		scrollable_treelist = Gtk.ScrolledWindow()
		scrollable_treelist.set_vexpand(True)
		grid.attach(scrollable_treelist, 0, 0, 8, 10)
		scrollable_treelist.add(treeview)

		# Show "app" qubes by default
		self.type_filter.refilter()
		self.vbox.pack_start(grid, True, True, 0)

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

	def create_footer(self):
		footer = Gtk.Box(spacing=10)
		footer.set_border_width(10)
		
		files = self.icon_button("Files", "system-file-manager")
		files.connect("clicked", self.on_button_clicked, "Files")
		footer.pack_start(files, False, False, 0)

		terminal = self.icon_button("Terminal", "utilities-terminal")
		terminal.connect("clicked", self.on_button_clicked, "Install Apps")
		footer.pack_start(terminal, False, False, 0)

		self.vbox.pack_start(footer, False, False, 0)

	def footer_button(self, label, icon):
		"""Renders button for footer"""
		button = Gtk.Button()
		image = Gtk.Image()

		image.set_from_icon_name(icon, Gtk.IconSize.BUTTON)
		image.show()
		image.set_margin_left(20)
		image.set_margin_right(20)
		
		button.set_label(label)
		button.set_image(image)
		button.set_relief(Gtk.ReliefStyle.NONE)

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

	def on_state_combo_changed(self, combo):
		"""Select filter combobox item"""
		self.current_filter_state = self.filter_states[combo.get_active()]
		self.current_filter = self.current_filter_state
		self.type_filter.refilter()

	def on_type_toggled(self, radio, new_type):
		"""Clicking filter type button"""
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

	def on_button_clicked(self, button, value):
		print "button clicked: %s" % value


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
