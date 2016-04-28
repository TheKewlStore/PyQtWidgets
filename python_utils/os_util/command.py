# coding=utf-8
""" Module Docstring.

Author: Ian Davis
Last Updated: 9/17/2015
"""

import os
import subprocess
import sys

import exceptions
import system


def command_line_arguments():
    """ Return the command line arguments passed when the script was run.
    """
    return sys.argv


def _format_argument_list(args):
    new_args = []
    for arg in args:
        new_args.append(str(arg))

    return new_args


def background_process(args):
    """ Run a shell command in the background.

    :param args: The arguments to pass to the command line.
    :raise NoArgumentError: If no command or arguments are supplied to run.
    """
    if not args:
        raise exceptions.NoArgumentError("No command or arguments supplied")

    formatted_args = _format_argument_list(args)
    return subprocess.Popen(formatted_args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)


def start_python_script(script_path):
    """ Run a python script in the background.

    :param script_path: The path to the script to run.
    """
    cmd = (sys.executable,
           script_path)

    formatted_args = _format_argument_list(cmd)

    return subprocess.Popen(formatted_args,
                            stdout=None,
                            stdin=None,
                            stderr=None)


def shell_command(args, console_window=False):
    """ Run a shell command.

    :param args: The arguments to pass to the command line.
    :param console_window: Whether or not to include a console window.
    :raise NoArgumentError: If no command or arguments are supplied to run.
    """
    if not args:
        raise exceptions.NoArgumentError("No command or arguments supplied")

    formatted_args = _format_argument_list(args)
    startup_info = None

    if system.windows_platform() and not console_window:
        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup_info.wShowWindow = subprocess.SW_HIDE

    process = subprocess.Popen(formatted_args,
                               cwd=os.getcwd(),
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               startupinfo=startup_info)

    std_out, std_err = process.communicate()
    exit_code = process.returncode

    return exit_code, std_out, std_err


def reboot():
    """ Reboot the local operating system.
    """
    if system.windows_platform():
        args = ('shutdown', '-r', '-t 1')
    else:
        args = ('reboot',)

    return shell_command(args)


def shutdown():
    """ Shutdown the local operating system.
    """
    args = ('shutdown', '-t 1')
    return shell_command(args)


def restart_script():
    os.execv(sys.executable, [sys.executable] + sys.argv)
