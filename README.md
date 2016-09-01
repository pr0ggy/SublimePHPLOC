![](https://img.shields.io/badge/version-1.0.0-blue.svg)

PHPLOC
===============

This plugin allows you the run PHPLOC straight from the Sublime Text interface.  
Built and tested using [PHPLOC 2.1.4](https://github.com/sebastianbergmann/phploc).


### Installation:
1. Use [Package Control](https://packagecontrol.io/installation) to install `PHPLOC`
2. Download and unzip the plugin files to `<Your ST2-ST3 Packages Directory>\SublimePHPLOC\`


### Usage:
1. Press Cmd + Shift + P to open the control palette
2. Search for `PHPLOC` and pick your command

Also you can use the `Tools --> PHPLOC...` menu item, or set up custom keybindings


### Available Palette Commands
**`Run On Project`**  
This is the equivalent of running:  `phploc [path to sublime project root directory]`

**`Run On Current File`**  
This is the equivalent of running:  `phploc [path to current file]`  
This command is only visible when the focused view contains a PHP file.

**`Run On Selection`**  
This option runs PHPLOC on the currently selected lines.  
This command is only visible when the focused view contains a PHP file.

You can also right-click a directory or PHP file in the sidebar and select **`Run PHPLOC`** from the context menu to run PHPLOC on that file/directory.  Note that this command will only appear when clicking PHP files; any other filetype will not allow selecting the command from the context menu.


### Keybinding:
You can also set up custom key bindings.

**Example: Setting up key binding to execute PHPLOC on current open project**:
```json
{
    "keys": ["ctrl+alt+l"],
    "command": "sublime_phploc_project"
}
```

**Commands that can be executed via key binds:**  
- `sublime_phploc_path`  
    *(can pass in a 'paths' argument with a list containing a single path...see 'Side Bar.sublime-menu' in source for skeleton example)*  
- `sublime_phploc_project`  
- `sublime_phploc_selected_lines`

### Changelog

**1.0.0**  
Added ability to execute PHPLOC on currently-selected text in PHP files  
Current file command only shows up if applicable (PHP file has focus)  
Module refactoring  

**0.9.1.1**  
Fixed incorrect package name in README install instructions (name changed before Package Control submission)

**0.9.1**  
Fixed missing `subprocess` module used when running on Windows OS

**0.9**  
Initial release
