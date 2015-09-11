'''Sublime plugin module which allows for the execution of PHPLOC against the open project or
a specific path (file or directory) from within Sublime.
'''

import os
import sublime
import sublime_plugin

class NoOpenProjectException(Exception):
    '''Exception for when no open project is found, but open project is required'''
    pass


class NoActiveFileException(Exception):
    '''Exception for when no active file view is detected, but one is required'''
    pass


class InvalidFileTypeException(Exception):
    '''Exception for when attempt is made to run a command on a file type not supported by the command'''
    pass


class BadPathException(Exception):
    '''Exception for when a malformed or otherwise invalid path is detected'''
    pass


def generate_base_command(executable_string):
    '''Function which generates a new PHPLOC command in list format

    By default, this contains only the executable string passed in
    '''
    return [executable_string]


class WindowOutputCommandExecuter:
    '''Basic, reusable shell command executer 

    Public Interface:
    run -- Executes a given command in a Sublime window and opens the output panel for output viewing
    '''

    def __init__(self, window, shell_command):
        '''WindowOutputCommandExecuter constructor

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

        self.panel = self.window.get_output_panel("exec")
        self.window.run_command("show_panel", {"panel": "output.exec"})


class SublimePhplocPathCommand(sublime_plugin.WindowCommand):
    '''sublime_plugin.WindowCommand subclass which runs PHPLOC on a given path

    Public Interface:
    run -- Executes PHPLOC command on the given path
    '''
    
    def __init__(self, *args, **kwargs):
        '''SublimePhplocPathCommand constructor

        Nothing to do here...command objects are instantiated once at the start of Sublime and when
        the plugin files (settings, .py files, etc)...not each time the command is invoked.  We want
        to read in the settings each time the command is launched to allow real-time editing of
        plugin settings without having to restart Sublime for them to be applied.
        '''
        super(SublimePhplocPathCommand, self).__init__(*args, **kwargs)
        print('SublimePhplocPathCommand instantiated')

    def run(self, *args, **kwargs):
        '''Executes PHPLOC command on the given path

        The path on which the command is executed depends on how the command is launched.  If launched
        from the context menu entry by right clicking in the sidebar, the clicked item path is passed
        into the object via the kwargs parameter ('paths' key...see `Side Bar.sublime-menu`).  If it
        is launched via the command palette, the path will be the file in the active view.  If any
        errors occur, a notification will be printed in the status bar.
        '''
        try:
            self._run_phploc(kwargs)
        except (IOError, InvalidFileTypeException, NoActiveFileException) as e:
            sublime.status_message(str(e))

    def _run_phploc(self, kwargs):
        self.config = sublime.load_settings('SublimePHPLOC.sublime-settings')
        current_file_path = self.window.active_view().file_name()
        explicit_path_list = kwargs.get('paths')
        run_path = current_file_path if explicit_path_list is None else explicit_path_list[0]
        self._validate_path(run_path)
        self._run_phploc_command(run_path)

    def _validate_path(self, path):
        if path is None:
            raise NoActiveFileException('PHPLOC Error: No path specified')
        elif os.path.isdir(path):
            pass
        elif os.path.isfile(path):
            if path.endswith('.php') is False:
                raise InvalidFileTypeException('PHPLOC can only be run on PHP files')
        else:
            raise BadPathException('PHPLOC Error: Bad path specified')

    def _run_phploc_command(self, full_file_path):
        try:
            command_exec = WindowOutputCommandExecuter(self.window, self._build_shell_command(full_file_path))
            command_exec.run()
        except (IOError) as e:
            raise IOError('IOError: PHPLOC command aborted');

    def _build_shell_command(self, full_file_path):
        command = generate_base_command(self.config.get('phploc_executable'))

        if full_file_path:
            command.append(full_file_path)

        return command


class SublimePhplocProjectCommand(sublime_plugin.WindowCommand):
    '''sublime_plugin.WindowCommand subclass which runs PHPLOC on the open project root

    Public Interface:
    run -- Executes PHPLOC command on the open project root
    '''

    def __init__(self, *args, **kwargs):
        '''SublimePhplocProjectCommand constructor

        Nothing to do here...command objects are instantiated once at the start of Sublime and when
        the plugin files (settings, .py files, etc)...not each time the command is invoked.  We want
        to read in the settings each time the command is launched to allow real-time editing of
        plugin settings without having to restart Sublime for them to be applied.
        '''
        super(SublimePhplocProjectCommand, self).__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        '''Executes PHPLOC command on open project root

        If a project is not open, a notification will be printed in the status bar.
        '''
        self.config = sublime.load_settings('SublimePHPLOC.sublime-settings')
        try:
            project_root_path = self._get_project_root()
            self._run_phploc(project_root_path)
        except (IOError, NoOpenProjectException) as e:
            sublime.status_message(str(e))

    def _get_project_root(self):
        try:
            project_root_path = self.window.folders()[0]
            return project_root_path
        except IndexError:
            raise NoOpenProjectException("PHPLOC must be run from an open Sublime project")

    def _run_phploc(self, project_root_path):
        try:
            command_exec = WindowOutputCommandExecuter(self.window, self._build_shell_command(project_root_path))
            command_exec.run()
        except (IOError) as e:
            raise IOError('IOError: PHPLOC command aborted');

    def _build_shell_command(self, project_root_path):
        command = generate_base_command(self.config.get('phploc_executable'))

        if project_root_path:
            command.append(project_root_path)

        return command
