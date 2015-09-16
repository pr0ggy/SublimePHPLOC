'''Sublime plugin module which allows for the execution of PHPLOC against
 - the open project
 - a specific path (file or directory)
 - the currently-selected text
 from within Sublime.
'''

import os
import subprocess
import sublime
import sublime_plugin

PLUGIN_DIRECTORY_PATH = os.path.dirname(os.path.abspath(__file__))


class InvalidPathException(Exception):
    '''Exception for when a malformed or otherwise invalid path is detected'''
    pass


class EmptyPathException(Exception):
    '''Exception for when an empty path is detected'''
    pass


class EmptySelectionException(Exception):
    '''Exception for when an empty path is detected'''
    pass


def get_st_command_explicit_or_implicit_path(explicit_path_list=None):
    '''Command that returns the path to be used when executing one of the below plugin commands.

    If a path is explicitly given, it will be in the explicit_path_list parameter (see
    `Side Bar.sublime-menu` for how paths of side bar items are explicitly passed into the command).
    If non are given, we can assume the command is to be run on the file in the active view.  If no
    such active view exists, simply return False.
    '''
    if explicit_path_list:
        return explicit_path_list[0]
    elif sublime.active_window().active_view().file_name():
        return sublime.active_window().active_view().file_name()
    else:
        return False

def verify_path_is_file_or_directory(path):
    '''Validates a path as a valid file or directory

    This implementation raises an EmptyPathException if an empty path is given and
    raises an InvalidPathException if an invalid path is given.
    '''
    if path is None:
        raise EmptyPathException('Empty path given')

    if not os.path.isdir(path) and not os.path.isfile(path):
        raise InvalidPathException('Invalid path given')

def verify_path_has_php_extension_of_pointing_to_file(path):
    '''Validates a path as having a '.php' extension

    This implementation raises an InvalidPathException if the path points to a file with
    anything other than a '.php' extension
    '''
    if os.path.isfile(path) and path.endswith('.php') is False:
        raise InvalidPathException('Given path is not a PHP file')

def generate_composite_path_validation_func(component_validation_funcs):
    '''Currying function which returns a function composite for path validation'''

    def composite_path_validation_func(path):
        '''Curried function which takes a path and executes the given component path validation
        functions against it
        '''
        [f(path) for f in component_validation_funcs]

    return composite_path_validation_func

# only need a single instance of this path validation function
# this can be pulled into the ST commands defined below for use
PHPLOC_PATH_VALIDATION = generate_composite_path_validation_func([
    verify_path_is_file_or_directory,
    verify_path_has_php_extension_of_pointing_to_file
])


class PathShellCommand(object):
    '''Simple class representing a shell command that is exectuted on a path (file/directory)

    Public Interface:
    as_executable_and_arg_list -- Returns the command executable, options, and path as a list
    '''

    def __init__(self, executable, option_list, path):
        '''PathShellCommand constructor

        Dependencies:
        executable -- The executable command as a string
        option_list -- All options (flags, k/v pairs, etc) associated with the command as a list
        path -- The path the command will be executed on as a string

        i.e. 'phploc --name=test.php,test2.php --progress "</path/to/directory/>"'
        executable = 'phploc'
        option_list = ['--name=test.php,test2.php', '--progress']
        path = '</path/to/directory/>'
        '''
        self.executable = executable
        self.executable_option_list = option_list
        self.path = path

    def as_executable_and_arg_list(self):
        '''Returns the command executable, options, and path as a list

        i.e. 'phploc --name=test.php,test2.php --progress "</path/to/directory/>"'
        returns ['phploc', '--name=test.php,test2.php', '--progress', '</path/to/directory/>']
        '''
        return [self.executable] + self.executable_option_list + [self.path]


class WindowOutputShellCommandExecuter(object):
    '''Basic, reusable shell command executer

    Public Interface:
    run -- Executes a given command in a Sublime window and opens the output panel for output viewing
    '''

    def __init__(self, window, shell_command):
        '''WindowOutputShellCommandExecuter constructor

        Dependencies:
        window -- A sublime.Window instance in which to run the command via the sublime.Window.run_command method
        shell_command -- The command to be executed, in list format (i.e. 'phpunit --stderr' = ['phpunit', '--stderr'])
        '''
        self.window = window
        self.shell_command = shell_command

    def run(self):
        '''Executes a given command in a Sublime window and opens the output panel for output viewing'''
        if os.name != 'posix':
            self.shell_command = subprocess.list2cmdline(self.shell_command)

        self.window.run_command("exec", {
            "cmd": self.shell_command,
            "shell": os.name == 'nt',
        })

        self.window.run_command("show_panel", {"panel": "output.exec"})


class SublimePhplocPathCommand(sublime_plugin.WindowCommand):
    '''sublime_plugin.WindowCommand subclass which runs PHPLOC on a given path

    Public Interface:
    is_enabled -- Returns boolean denoting whether or not a command is available for execution
    run -- Executes PHPLOC command on the given path
    '''

    def __init__(self, *args, **kwargs):
        super(SublimePhplocPathCommand, self).__init__(*args, **kwargs)
        self.path_validation = PHPLOC_PATH_VALIDATION # single instance defined at module level

    def is_enabled(self, paths=None):
        '''Override of sublime_plugin.WindowCommand.is_enabled()

        Ran whenever Sublime needs to know whether or not this specific command can be
        executed or shown as an option in the command palette.
        '''
        try:
            self.path_validation(get_st_command_explicit_or_implicit_path(paths))
            return True
        except:
            return False

    def run(self, *args, **kwargs):
        '''Executes PHPLOC command on the given path

        The path on which the command is executed depends on how the command is launched.  If
        launched from the context menu entry by right clicking in the sidebar, the clicked item
        path is passed into the object via the kwargs parameter ('paths' key...see
        `Side Bar.sublime-menu`).  If it is launched via the command palette, the path will be the
        file in the active view.  If any errors occur, a notification will be printed in the
        status bar.
        '''
        self.config = sublime.load_settings('SublimePHPLOC.sublime-settings')
        try:
            self._run_phploc(kwargs)
        except (IOError, InvalidPathException) as exception:
            sublime.status_message(str(exception))
        except (EmptyPathException) as exception:
            sublime.status_message('PHPLOC must be run on a PHP file or directory')

    def _run_phploc(self, kwargs):
        '''Determines path on which to run the phploc command, and executes it'''
        # see `Side Bar.sublime-menu` for how paths of side bar items are explicitly passed into the command
        explicit_path_list = kwargs.get('paths')
        run_path = get_st_command_explicit_or_implicit_path(explicit_path_list)
        self.path_validation(run_path)

        command = PathShellCommand(self.config.get('phploc_executable'), [], run_path)
        command_exec = WindowOutputShellCommandExecuter(self.window, command.as_executable_and_arg_list())
        command_exec.run()


class SublimePhplocProjectCommand(sublime_plugin.WindowCommand):
    '''sublime_plugin.WindowCommand subclass which runs PHPLOC on the open project root

    Public Interface:
    is_enabled -- Returns boolean denoting whether or not a command is available for execution
    run -- Executes PHPLOC command on the open project root
    '''

    def is_enabled(self):
        '''Override of sublime_plugin.WindowCommand.is_enabled()

        Ran whenever Sublime needs to know whether or not this specific command can be
        executed or shown as an option in the command palette.
        '''

        # we only want this command enabled if an open project exists in the current window
        try:
            # below line raises IndexError if no folders exist (no open project)
            project_root_path = self.window.folders()[0]
            return True
        except IndexError:
            return False

    def run(self):
        '''Executes PHPLOC command on open project root

        If a project is not open, a notification will be printed in the status bar.
        '''
        try:
            self._run_phploc()
        except IOError as io_exception:
            sublime.status_message(str(io_exception))
        except IndexError:
            sublime.status_message('No open projects found')

    def _run_phploc(self):
        '''Executes the current window's SublimePhplocPathCommand instance on the current project
        root's path
        '''
        # below line raises IndexError if no folders exist (no open project)
        project_root_path = self.window.folders()[0]
        self.window.run_command('sublime_phploc_path', {
            'paths': [project_root_path]
        })


class SublimePhplocSelectedLinesCommand(sublime_plugin.WindowCommand):
    '''sublime_plugin.WindowCommand subclass which runs PHPLOC on currently-selected lines

    Public Interface:
    is_enabled -- Returns boolean denoting whether or not a command is available for execution
    run -- Executes PHPLOC on currently-selected lines
    '''

    def __init__(self, *args, **kwargs):
        '''SublimePhplocSelectedLinesCommand constructor

        There are no explicit dependencies here, we just set the path of the file where the plugin
        will copy the current selection before running PHPLOC as this file path will not change.
        '''
        super(SublimePhplocSelectedLinesCommand, self).__init__(*args, **kwargs)
        self.path_validation = PHPLOC_PATH_VALIDATION # single instance defined at module level
        self.SELECTION_FILE_PATH = os.path.join(PLUGIN_DIRECTORY_PATH, 'selection.php')

    def is_enabled(self, paths=None):
        '''Override of sublime_plugin.WindowCommand.is_enabled()

        Ran whenever Sublime needs to know whether or not this specific command can be
        executed or shown as an option in the command palette.
        '''

        # only enable if text is currently selected in an open PHP file
        try:
            self.path_validation(get_st_command_explicit_or_implicit_path(paths))
            self._verify_selection_exists()
            return True
        except:
            return False

    def _verify_selection_exists(self):
        '''Ensures that selected regions exist in the current view

        If no selected regions are found, an EmptySelectionException is thrown
        '''
        for region in self.window.active_view().sel():
            if not region.empty():
                return

        raise EmptySelectionException('Nothing selected')

    def run(self):
        '''Executes PHPLOC command on currently-selected text

        If no selected text, a notification will be printed in the status bar.
        '''
        try:
            self._run_phploc()
        except (
                IOError,
                EmptySelectionException,
                EmptyPathException,
                InvalidPathException
            ) as exception:
            sublime.status_message(str(exception))

    def _run_phploc(self):
        '''Validates that PHPLOC can be run on the current selection and runs the command on
        the selection if so
        '''
        self.path_validation(get_st_command_explicit_or_implicit_path())
        self._verify_selection_exists()
        self._write_selection_to_file()
        self._run_phploc_on_selection_file()

    def _write_selection_to_file(self):
        '''Pulls the currently selected lines out into a separate file on which a path command
        can be run'''
        selection_output_file_handle = open(self.SELECTION_FILE_PATH, 'w')
        selection_lines = self.get_current_selection_lines()
        if not selection_lines[0].strip().startswith('<?'):
            # selection file has to start with PHP tag
            selection_output_file_handle.write("<?php\n\n")

        [selection_output_file_handle.write(line) for line in selection_lines]

        selection_output_file_handle.close()

    def get_current_selection_lines(self):
        '''Gets the currently selected lines of text'''
        active_view = self.window.active_view()
        get_region_line = lambda region: (active_view.substr(active_view.line(region)) + "\n")
        return [get_region_line(region) for region in active_view.sel()]

    def _run_phploc_on_selection_file(self):
        '''Simply executes a SublimePhplocPathCommand against the generated file containing the
        user's selected text when the plugin command was invoked'''
        self.window.run_command('sublime_phploc_path', {
            'paths': [self.SELECTION_FILE_PATH]
        })
