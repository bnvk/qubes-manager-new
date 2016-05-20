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

I'm going to keep track of micro tasks / things i'm implementing in this here
README instead of Github issues as no sense in cluttering up things.

### Manager

- [x] convert sub menu Applications to Glade
- [x] convert sub menu Networking to Glade
- [x] convert sub menu Templates to Glade
- [x] get main navbar to use Glade
- [x] make "state" button show default state "All"
- [x] add devices and drives to footer
- [x] make clicking on "qube" open "overview window"
- [-] make "qube" color reflect on/off state
- [-] make background of qubes scrollable matching
- [ ] add "right-click" menu to each qube


### Overview

- [x] plumb in test data for a specific "qube"

### Advanced

- [-] create scaffolding for each view
- [ ] add to existing code

### Recipes

- [-] create scaffolding
- [ ] create header with main toggle buttons
- [ ] create filterable (un/installed) view of recipes
- [ ] implement install / uninstall state

### Backups

- [-] create scaffolding for Backups

### Settings

- [x] create scaffolding for global Setting


