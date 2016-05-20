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

# Test Data

class BackupsHandler(Gtk.Window):

	def run_toggle(self, toggle, state):
		print "toggled run_toggle: %s" % state


class BackupsWindow(Gtk.Window):

	def __init__(self):

		# Load Glade UI
		self.builder = Gtk.Builder()

		try:
			self.builder.add_from_file("glade/backups.glade")
		except:
			print("glade file not found")
			sys.exit()

		self.builder.connect_signals(BackupsHandler())

		# Create Window
		window = self.builder.get_object("windowBackups")	
		window.set_position(Gtk.WindowPosition.CENTER)
		window.set_default_size(500, 450)
		window.set_resizable(True)
		
		# Close Window & Show
		window.connect("delete-event", Gtk.main_quit)
		window.show()


def main():

	win = BackupsWindow()
	Gtk.main()

if __name__ == "__main__":
    main()
