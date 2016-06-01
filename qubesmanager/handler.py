#!/usr/bin/python2
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2016 Brennan Novak <bnvk@invisiblethingslab.com>

# Gtk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio

class ManagerHandler():

	def launchAbout(self, button):
		print "launch About window"

	def toggleQubeType(self, toggle):
		print "toggle qube type"
		self.current_filter_state = self.filter_states[combo.get_active()]
		self.current_filter = self.current_filter_state
		self.type_filter.refilter()

	def launchRecipes(self, button):
		print "launch Recipes window"

	def launchBackups(self, button):
		print "launch Backups window"

	def launchHelp(self, button):
		print "launch Help window"

	def launchSettings(self, button):
		print "launch Settings window"

	def installApps(self, button):
		print "install apps"

	def attachMicrophone(self, button):
		print "attach microphone"

	def createQube(self, button):
		print "create Qube window"

	def toggleQubeState(self, toggle):
		print "launch  window"
