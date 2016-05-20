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
from gi.repository import Gtk, Gdk, Gio
from gi.repository.GdkPixbuf import Pixbuf

# Qubes Test Data
import tests.data_vmcollection
qvm_collection = tests.data_vmcollection

class AdvancedHandler(Gtk.Window):

	def on_clicked(self, button):
		print "on clicked"

class AdvancedWindow(Gtk.Window):

	def __init__(self, qube_name):

		# Load Glade UI
		builder = Gtk.Builder()

		try:
			builder.add_from_file("glade/advanced.glade")
		except:
			print("glade file not found")
			sys.exit()

		builder.connect_signals(AdvancedHandler())

		# Create Window
		window = builder.get_object("advancedWindow")
		window.set_position(Gtk.WindowPosition.CENTER)
		window.set_default_size(500, 450)
		window.set_resizable(False)

		# Close Window
		window.connect("delete-event", Gtk.main_quit)
		window.show_all()

def main(qube_name):

	win = AdvancedWindow(qube_name)
	Gtk.main()

if __name__ == "__main__":
	main()
