Qubes Manager
=============

A new user friendly GUI qube manager for Qubes OS

Make sure you have Gtk+3 installed. Then to run the main Qubes Manager window
run from the main directory

```
cd qubes-manager-new
chmod 775 qubes-manager qubes-manager-overview qubes-manager-advanced
```

To run each part of the app, do the following:

```
./qubes-manager
./qubes-manager-overview qube-name
./qubes-manager-advanced qube-name
```

---


## ToDo

This is a list of micro tasks / things i'm implementing

### Manager

- [-] make "qube" color reflect on/off state
- [-] make background of qubes scrollable matching
- [ ] add "right-click" menu to each qube
- [ ] Add items from existing VM Manager to main titlebar menus
- [ ] Rethink purpose / existence of footer bar with differing qubes / dom0
- [ ] Tuck away dom0 shortcuts from footer bar
- [ ] Move "Updates" to topbar
- [ ] Move dom0 Terminal & File Manager to Settings diaglog
- [ ] Modify Applications "install apps" button or launcher
- [ ] Change status and qube of the "attached" microphone button
- [ ] Implement qube color label (easier to identify in grid) 
- [ ] Display qube state (halted, etc...) like a tiny icon
- [ ] Make hovering over qube trigger a color change ????


### Manager - About

- [ ] Add version of Qubes OS
- [ ] Add button to bug reporting tool
- [ ] Remove the hyperlink as it is useless in dom0


### Manager - Devices

- [ ] How to "attach block device to qube" either drag & drop or pick from list
- [ ] How to "attach non-block devices" like keyboards to other qubes
- [ ] Allow only attaching of one device to one qube (not mic & usb)
- [ ] Move sys-device qubes elsewhere (networking / devices)
- [ ] Add microphone & camera to "device" qube icons (all are attachable)

> what happens technically when a block device is attached to a qube? Is no
> longer available back in sys-usb, right?  Should this be easy to switch back?

> Make the shortcut footer bar swap out when a "qube" is selected 
> Show things like (Files, Terminal, Etc...)
> Not sure if this is a good idea, using Gnomes default thing is prolly better


### Manager - Application

- [ ] Integrate Standalone Qubes with a visual distinction


### Manager - Networking

> Maybe move "Captive Portal" to device footer bar with "Get Online"


### Manager - Settings

> You said: "updates: Tor" may require better description
> What is the risks / cases of "where else" one might want to run updates?

- [ ] Add little "?" explainer bubbles
- [ ] Make closing dialog kill instance
- [ ] Make Cancel & Save buttons trigger events 

> there is no per-VM clock vm - there is only one global, so not the best 
> under "Default Qubes"  so what's the deals with Clock VM? Considerations


### Create Qube

- [ ] Have a step to pick icon from a list


### Qube Overview

- [ ]  Add list of "shortcut" application menus (test long file names)
- [ ] Convert Wifi & Ethernet and Firewall into just Clearnet selection
- [ ] Add % label for disk space
- [ ] Make color of disk space bar change 
- [ ] Use alternate (not sliders) for re-sizing disk space selection
- [ ] Add limiters on re-size disk space size (don't allow shrinking)
- [ ] Make "Backup Now" launch backup tool with selected window
- [ ] Make icon reflect status
- [ ] Add category (App, Standlone, Net, Template) sub-title text 

> Marek: on/off - not sure about usefulness of this


### Qube Advanced

- [-] create scaffolding for each view
- [ ] add to existing code


### Recipes

- [-] create scaffolding
- [ ] create header with main toggle buttons
- [ ] create filterable (un/installed) view of recipes
- [ ] implement install / uninstall state

> Consider "Update" button, which a recipe itself could update (new feature,
> configuration, etc...) and user may not want to update automatically


### Backups

- [-] create scaffolding for Backups


