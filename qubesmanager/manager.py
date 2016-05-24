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

import qubesmanager.overview
qube_overview = qubesmanager.overview

import qubesmanager.recipes
qubes_recipes = qubesmanager.recipes

import qubesmanager.backups
qubes_backups = qubesmanager.backups


class ManagerWindow(object):

	def __init__(self, app):

		# Load Glade UI
		self.builder = Gtk.Builder()
		self.builder.add_from_file("glade/manager.glade")

		# Setup Window
		self.window = self.builder.get_object("managerWindow")

		# Add Events
		self.builder.connect_signals(self)

		self.vbox = self.builder.get_object("vbox")

		self.qubesTabs = self.builder.get_object("qubesTabs")

		# ListStore of qubes
		self.qubes_liststore = self.builder.get_object("qubes_liststore")

		for qube in qvm_collection.values():
			if qube["icon"] != "default":
				image = qube["icon"]
			else:
				image = "qube-32"
			pixbuf = Pixbuf.new_from_file("icons/" + image + ".png")

			# TODO: make qube icon reflect machine state
			# 'Halted'		Machine is not active
			# 'Transient'	Machine is running, not have guid or qrexec
			# 'Running'		Machine is ready and running.
			# 'Paused'		Machine is paused (currently not available, see below)
			# 'Suspended'	Machine is S3-suspended
			# 'Halting'		Machine is in process of shutting down
			# 'Dying'		Machine crashed and is unusable
			# 'Crashed'		Machine crashed and is unusable
			# 'NA'			Machine is in unknown state

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
		self.type_filter = self.builder.get_object("type_filter")
		self.type_filter.set_visible_func(self.type_filter_func)

		# Main Grid of qubes
		self.create_qube_grid()

		footerBox = self.builder.get_object("footerBox")

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

		footerBox.pack_end(self.builder.get_object("systemButtons"), False, False, 0)
		self.vbox.pack_end(footerBox, False, False, 0)

		# Check for Updates
		# TODO: this should call out to check status somewhere
		imageDom0Update = self.builder.get_object("imageDom0Update")
		imageDom0Update.set_from_icon_name("software-update-available", 32)
		buttonDom0Updates = self.builder.get_object("buttonDom0Updates")
		buttonDom0Updates.set_label("Update Now")

		# Show All
		self.window.show_all()

	def create_qube_grid(self):
		"""Renders filterable IconView in a grid of qubes"""

		iconview = self.builder.get_object("iconview")

		# Choose Icon & Text value in list
		iconview.set_pixbuf_column(3)
		iconview.set_text_column(1)

		# Focus and show "app" qubes
		iconview.grab_focus()
		self.type_filter.refilter()

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

	def gtk_main_quit(self, *args):
		return Gtk.main_quit(*args)

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

		type_to_page = {
			'app': 0,
			'net': 1,
			'template': 2,
		}
		self.qubesTabs.set_current_page(type_to_page[new_type])

	def on_tab_change(self, noteboot, page, page_num):
		self.current_filter_type = ['app', 'net', 'template'][page_num]
		self.current_filter = self.current_filter_type
		self.type_filter.refilter()

	def on_qube_item_double_click(self, icon_view, tree_path):
		print "Item double-clicked name: %r" % self.qubes_liststore[tree_path][2]
		qube_overview.main(self.qubes_liststore[tree_path][2])

	def on_qube_item_single_click(self, iconview, event):
		if event.button == 3:
			print "Grid item single clicked RIGHT"
		else:
			print "Grid item single clicked LEFT"

	# Toolbar Buttons
	def on_clicked_launch_recipes(self, button):
		print "launch Recipes"
		qubes_recipes.main()

	def on_clicked_launch_backups(self, button):
		print "launch Backups"
		qubes_backups.main()

	def on_clicked_launch_help(self, button):
		print "launch Help"

	def on_clicked_launch_settings(self, button):
		print "Launch SettingsDialog"
		dialogSettings = self.builder.get_object("dialogGlobalSettings")
		dialogSettings.set_default_size(500, 350)
		dialogSettings.set_title("Qubes Settings")
		dialogSettings.set_border_width(15)

		# Various comboboxes
		comboSettingsFiles = self.builder.get_object("comboSettingsFiles")
		comboSettingsBrowser = self.builder.get_object("comboSettingsBrowser")
		comboSettingsText = self.builder.get_object("comboSettingsText")
		comboSettingsTerminal = self.builder.get_object("comboSettingsTerminal")

		comboSettingsUpdates = self.builder.get_object("comboSettingsUpdates")
		comboSettingsClock = self.builder.get_object("comboSettingsClock")
		comboSettingsNetworking = self.builder.get_object("comboSettingsNetworking")
		comboSettingsTemplate = self.builder.get_object("comboSettingsTemplate") 
		comboSettingsKernel = self.builder.get_object("comboSettingsKernel")
		
		# Populate & Pick "qube" comboboxes
		for this_qube in qvm_collection.values():

			comboSettingsUpdates.append_text(this_qube["desc"])
			comboSettingsClock.append_text(this_qube["desc"])

			if this_qube["type"] == "net":
				comboSettingsNetworking.append_text(this_qube["desc"])

			if this_qube["type"] == "template":
				comboSettingsTemplate.append_text(this_qube["desc"])

		comboSettingsFiles.set_active(0)
		comboSettingsBrowser.set_active(0)
		comboSettingsText.set_active(0)
		comboSettingsTerminal.set_active(1)

		comboSettingsUpdates.set_active(10)
		comboSettingsClock.set_active(7)
		comboSettingsNetworking.set_active(3)
		comboSettingsTemplate.set_active(1)

		# Kernel
		comboSettingsKernel.append_text("4.1.13-9")
		comboSettingsKernel.set_active(0)

		# Memory Settings
		spinSettingsMemMin = self.builder.get_object("spinSettingsMemMin")
		spinSettingsMemBoost = self.builder.get_object("spinSettingsMemBoost")

		mem_min_adjustment = Gtk.Adjustment(0, 0, 100, 1, 10, 0)
		mem_boost_adjustment = Gtk.Adjustment(0, 0, 100, 1, 10, 0)

		spinSettingsMemMin.set_adjustment(mem_min_adjustment)
		spinSettingsMemBoost.set_adjustment(mem_boost_adjustment)

		# Show It
		dialogSettings.show()

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
	def on_clicked_dom0_updates(self, button):
		print "launch dom0 updates"
	
	def on_clicked_dom0_files(self, button):
		print "launch dom0 file browser"

	def on_clicked_dom0_terminal(self, button):
		print "launch dom0 terminal"


class QubesManager(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self,
								 application_id="org.invisiblethingslab.qubes",
								 flags=Gio.ApplicationFlags.FLAGS_NONE)

	def do_activate(self):
		win = ManagerWindow(self)
		win.window.show_all()

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
		print("clicked: show qube Overview: %s" % parameter)
		#qube_overview.main(store_item[tree_path][2])

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


def run():
    app = QubesManager()
    app.run(sys.argv)
    Gtk.main()
