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

class OverviewHandler(Gtk.Window):

	def runToggle(self, toggle):
		print "toggled runToggle"

	def networkManage(self, toggle):
		print "toggled networkManage"

	def updateNow(self, button):
		print "clicked updateNow"

	def editDiskSpace(self, button):
		print "clicked editDiskSpace"

	def deleteQube(self, button):
		print "clicked deleteQube"


# Load Glade UI
builder = Gtk.Builder()

try:
	builder.add_from_file("glade/overview.glade")
except:
	print("glade file not found")
	sys.exit()

builder.connect_signals(OverviewHandler())

window = builder.get_object("qubeOverview")
window.show_all()
window.connect("delete-event", Gtk.main_quit)
window.show_all()

Gtk.main()
