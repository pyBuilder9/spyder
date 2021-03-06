# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
Internal Console Plugin.
"""

# Standard library imports
import logging

# Third party imports
from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon

# Local imports
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.translations import get_translation
from spyder.plugins.console.widgets.main_widget import ConsoleWidget


# Localization
_ = get_translation('spyder')


# Logging
logger = logging.getLogger(__name__)


class Console(SpyderDockablePlugin):
    """
    Console widget
    """
    NAME = 'internal_console'
    WIDGET_CLASS = ConsoleWidget
    CONF_SECTION = NAME
    CONF_FILE = False
    CONF_FROM_OPTIONS = {
        'color_theme': ('appearance', 'selected'),
    }
    TABIFY = [Plugins.IPythonConsole, Plugins.History]

    # --- Signals
    # ------------------------------------------------------------------------

    # This signal will request to open a file in a given row and column
    # using a code editor.
    sig_edit_goto_requested = Signal(str, int, str)

    # TODO: I think this is not being used now?
    sig_focus_changed = Signal()

    # Emit this when the interpreter buffer is flushed
    sig_refreshed = Signal()

    # --- SpyderDockablePlugin API
    # ------------------------------------------------------------------------
    def get_name(self):
        return _('Internal console')

    def get_icon(self):
        return QIcon()

    def get_description(self):
        return _('Internal console running Spyder.')

    def register(self):
        widget = self.get_widget()

        # Signals
        widget.sig_edit_goto_requested.connect(self.sig_edit_goto_requested)
        widget.sig_focus_changed.connect(self.sig_focus_changed)
        widget.sig_quit_requested.connect(self.sig_quit_requested)
        widget.sig_refreshed.connect(self.sig_refreshed)

        # Crash handling
        previous_crash = self.get_conf_option(
            'previous_crash',
            default='',
            section='main',
        )
        if previous_crash:
            widget.handle_exception(
                text=previous_crash,
                is_traceback=True,
                is_faulthandler_report=True,
            )

    def update_font(self):
        font = self.get_font()
        self.get_widget().set_font(font)

    def on_close(self, cancelable=False):
        self.get_widget().dialog_manager.close_all()
        return True

    # --- API
    # ------------------------------------------------------------------------
    @property
    def error_dialog(self):
        """
        Error dialog attribute accesor.
        """
        return self.get_widget().error_dlg

    def close_error_dialog(self):
        """
        Close the error dialog if visible.
        """
        self.get_widget().close_error_dlg()

    def exit_interpreter(self):
        """
        Exit the internal console interpreter.

        This is equivalent to requesting the main application to quit.
        """
        self.get_widget().exit_interpreter()

    def execute_lines(self, lines):
        """
        Execute the given `lines` of code in the internal console.
        """
        self.get_widget().execute_lines(lines)

    def get_sys_path(self):
        """
        Return the system path of the internal console.
        """
        return self.get_widget().get_sys_path()

    def handle_exception(self, text, is_traceback, is_pyls_error=False,
                         is_faulthandler_report=False):
        """
        Handle any exception that occurs during Spyder usage.
        """
        self.get_widget().handle_exception(
            text=text,
            is_traceback=is_traceback,
            is_pyls_error=is_pyls_error,
            is_faulthandler_report=is_faulthandler_report,
        )

    def quit(self):
        """
        Send the quit request to the main application.
        """
        self.sig_quit_requested.emit()

    def restore_stds(self):
        """
        Restore stdout and stderr when using open file dialogs.
        """
        self.get_widget().restore_stds()

    def redirect_stds(self):
        """
        Redirect stdout and stderr when using open file dialogs.
        """
        self.get_widget().redirect_stds()

    def set_exit_function(self, func):
        """
        Set the callback function to execute when the `exit_interpreter` is
        called.
        """
        self.get_widget().set_exit_function(func)

    def start_interpreter(self, namespace):
        """
        Start the internal console interpreter.

        Stdin and stdout are now redirected through the internal console.
        """
        widget = self.get_widget()
        widget.change_option('namespace', namespace)
        widget.start_interpreter(namespace)

    def set_namespace_item(self, name, value):
        """
        Add an object to the namespace dictionary of the internal console.
        """
        self.get_widget().set_namespace_item(name, value)
