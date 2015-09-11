![](https://img.shields.io/badge/version-0.9.1.1-yellowgreen.svg)

SublimePHPLOC
===============

This plugin allows you the run PHPLOC straight from the Sublime Text interface.  
Built and tested using [PHPLOC 2.1.4](https://github.com/sebastianbergmann/phploc).


### Available commands
**`Run On Project`**  
This is the equivalent of running:  `phploc [path to sublime project root directory]`

**`Run On Current File`**  
This is the equivalent of running:  `phploc [path to current file]`

You can also right-click a file/directory in the sidebar and select **`Run PHPLOC`** from the context menu to run PHPLOC on that file/directory.


### Installation:
1. Use [Package Control](https://packagecontrol.io/installation) to install `PHPLOC`
2. Download and unzip the plugin files to `<Your ST2-ST3 Packages Directory>\SublimePHPLOC\`


### Usage:
1. Press Cmd + Shift + P to open the control palette
2. Search for `PHPLOC` and pick your command

Also you can use the `Tools --> PHPLOC...` menu item, or set up custom keybindings


### Keybinding:
You can also set up custom key bindings.

**Example: Setting up key binding to execute PHPLOC on current open project**:
```json
{
    "keys": ["ctrl+alt+l"],
    "command": "sublime_phploc_project"
}
```


### Donate:
If you liked this plugin, feel free to donate! Expect regular maintenance, bugfixes, and updates!

[![Paypal donate](https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.me/JLueken)


### Changelog

**V0.9.1.1**  
Fixed incorrect package name in README install instructions (name changed before Package Control submission)

**V0.9.1**  
Fixed missing `subprocess` module used when running on Windows OS

**V0.9**  
Initial release
