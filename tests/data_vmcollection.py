# Test Data

def values():
	vms = [{
		"type": "app",
		"icon": "anonymous-32",
		"name": "web-anon",
		"desc": "Web Anonymous",
		"get_power_state": "Running",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": True,
		"is_outdated": True,
		"updateable": False
	},{
		"type": "app",
		"icon": "bitcoin-32",
		"name": "bitcoin",
		"desc": "Bitcoin",
		"get_power_state": "Halted",
		"is_fully_usable": False,
		"is_guid_running": False,
		"is_networked": True,
		"is_outdated": False,
		"updateable": False
	},{
		"type": "app",
		"icon": "vault-32",
		"name": "vault",
		"desc": "Vault",
		"get_power_state": "Running",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": False,
		"is_outdated": True,
		"updateable": False
	},{
		"type": "app",
		"icon": "mailpile-32",
		"name": "mailpile",
		"desc": "Mailpile",
		"get_power_state": "Running",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": True,
		"is_outdated": True,
		"updateable": False
	},{
		"type": "app",
		"icon": "default",
		"name": "email-work",
		"desc": "Email Work",
		"get_power_state": "Halted",
		"is_fully_usable": False,
		"is_guid_running": False,
		"is_networked": True,
		"is_outdated": False,
		"updateable": False
	},{
		"type": "app",
		"icon": "default",
		"name": "personal",
		"desc": "Personal",
		"get_power_state": "Halted",
		"is_fully_usable": False,
		"is_guid_running": False,
		"is_networked": False,
		"is_outdated": False,
		"updateable": False
	},{
		"type": "app",
		"icon": "qube-color-32",
		"name": "dev",
		"desc": "Development",
		"get_power_state": "Running",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": True,
		"is_outdated": False,
		"updateable": False
	},{
		"type": "net",
		"icon": "default",
		"name": "sys-net",
		"desc": "Wifi & Ethernet",
		"get_power_state": "Running",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": True,
		"is_outdated": True,
		"updateable": False
	},{
		"type": "net",
		"icon": "default",
		"name": "sys-firewall",
		"desc": "Firewall",
		"get_power_state": "Running",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": True,
		"is_outdated": True,
		"updateable": False
	},{
		"type": "net",
		"icon": "default",
		"name": "sys-whonix",
		"desc": "Tor Routing",
		"get_power_state": "Running",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": True,
		"is_outdated": False,
		"updateable": False
	},{
		"type": "sys",
		"icon": "usb-32",
		"name": "usbdata",
		"desc": "USB",
		"get_power_state": "Running",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": False,
		"is_outdated": False,
		"updateable": False
	},{
		"type": "sys",
		"icon": "sd-card-32",
		"name": "sddata",
		"desc": "SD Card",
		"get_power_state": "Running",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": False,
		"is_outdated": False,
		"updateable": False
	},{
		"type": "dev",
		"icon": "harddrive-32",
		"name": "usbdata",
		"desc": "Main Backup",
		"get_power_state": "Mounted",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": False,
		"is_outdated": False,
		"updateable": False
	},{
		"type": "template",
		"icon": "fedora-32",
		"name": "fedora-23",
		"desc": "Fedora",
		"get_power_state": "Halted",
		"is_fully_usable": False,
		"is_guid_running": False,
		"is_networked": True,
		"is_outdated": False,
		"updateable": False
	},{
		"type": "template",
		"icon": "debian-32",
		"name": "debian-8",
		"desc": "Debian",
		"get_power_state": "Halted",
		"is_fully_usable": False,
		"is_guid_running": False,
		"is_networked": True,
		"is_outdated": False,
		"updateable": True
	},{
		"type": "template",
		"icon": "template-32",
		"name": "whonix-gw",
		"desc": "Whonix Gateway",
		"get_power_state": "Running",
		"is_fully_usable": True,
		"is_guid_running": True,
		"is_networked": True,
		"is_outdated": False,
		"updateable": False
	}]
	return vms
