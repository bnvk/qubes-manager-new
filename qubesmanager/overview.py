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

import qubesmanager.advanced
qube_advanced = qubesmanager.advanced

class OverviewHandler(Gtk.Window):

	def run_toggle(self, toggle, state):
		print "toggled run_toggle: %s" % state

	def network_manage(self, combo):
		print "combo network_manage active: %r" % combo.get_active()

	def update_now(self, button):
		print "clicked update_now"

	def edit_disk_space(self, button):
		print "clicked edit_disk_space"

	def clone_qube(self, button):
		print "clicked clone_qube"

	def delete_qube(self, button):
		print "clicked delete_qube"

	def qube_advanced(self, button):
		print "clicked show advanced"
		qube_advanced.main()

	def show_qube_title(self, label):
		print "show qube title"

	def on_move_cursor(self, label):
		print "on_move_cursor"

	def close_overview_window(self, button, event):
		print "close Overview"


class OverviewWindow(Gtk.Window):

	def __init__(self, qube_name):

		# Load Glade UI
		self.builder = Gtk.Builder()

		try:
			self.builder.add_from_file("glade/overview.glade")
		except:
			print("glade file not found")
			sys.exit()

		self.builder.connect_signals(OverviewHandler())

		# Create Window
		window = self.builder.get_object("qubeOverview")	
		window.set_position(Gtk.WindowPosition.CENTER)
		window.set_default_size(500, 450)
		window.set_resizable(True)

		# Get qube data
		qube = qvm_collection.get_qube_by_name(qube_name)

		# Update UI
		if qube["icon"] != "default":
			image = qube["icon"]
		else:
			image = "qube-32"

		titleImage = self.builder.get_object("titleImage")
		titleImage.set_from_file("icons/" + image + ".png")

		titleLabel = self.builder.get_object("titleLabel")
		titleLabel.set_label(qube["desc"])

		runningSwitch = self.builder.get_object("runningSwitch")

		# State/status items
		if (qube["is_guid_running"] == True and
			qube["get_power_state"] == "Running"):
			runningSwitch.set_active(True)
		else:
			runningSwitch.set_active(False)	

		# Networking
		comboBoxNetworking = self.builder.get_object("comboBoxNetworking")
		# Get NetVMs to populate & select ID
		net_qube_id = 0
		selected_qube_id = 0
		for this_qube in qvm_collection.values():

			# TODO: will need to replace with better filtering / new API
			if this_qube["type"] == "net":
				comboBoxNetworking.append_text(this_qube["desc"])
				net_qube_id += 1
				if this_qube["name"] == qube["netvm"]:
					selected_qube_id = net_qube_id
		comboBoxNetworking.set_active(selected_qube_id)
		
		# Last Run
		last_run = time.strftime('%d %b, %Y',
								 time.localtime(qube["last_run_timestamp"]))
		labelLastRun = self.builder.get_object("labelLastRun")
		labelLastRun.set_label(last_run)

		# Disk Space
		diskSpace = self.builder.get_object("levelbarDiskSpace")
		diskSpace.set_value(qvm_collection.get_disk_utilization(qube))
		diskSpace.set_max_value(qvm_collection.get_private_img_sz(qube))

		# Backups
		last_backup = time.strftime('%d %b, %Y',
								 time.localtime(qube["backup_timestamp"]))
	 	labelBackupDate = self.builder.get_object("labelBackupDate")
		labelBackupDate.set_label(last_backup)

		# Type Options
		if qube["type"] == "app":
			self.builder.get_object("gridOptionsApplication").show()
		elif qube["type"] == "net":
			self.builder.get_object("gridOptionsNetworking").show()
		elif qube["type"] == "template":
			self.builder.get_object("gridOptionsTemplate").show()
		else:
			pass

		# Close Window & Show
		window.connect("delete-event", Gtk.main_quit)
		window.show()


def main(qube_name):

	win = OverviewWindow(qube_name)
	Gtk.main()

if __name__ == "__main__":
    main()
