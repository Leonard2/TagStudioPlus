# Copyright (C) 2024 Travis Abendshien (CyanVoxel).
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from typing import override

import structlog
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel, QWidget

from tagstudio.qt.helpers.silent_popen import silent_Popen

logger = structlog.get_logger(__name__)


def open_file(path: str | Path, file_manager: bool = False):
    """Open a file in the default application or file explorer.

    Args:
        path (str): The path to the file to open.
        file_manager (bool, optional): Whether to open the file in the file manager
            (e.g. Finder on macOS). Defaults to False.
    """
    path = Path(path)
    logger.info("Opening file", path=path)
    if not path.exists():
        logger.error("File not found", path=path)
        return

    try:
        if sys.platform == "win32":
            normpath = str(Path(path).resolve())
            if file_manager:
                command_name = "explorer"
                command_arg = f'/select,"{normpath}"'

                # For some reason, if the args are passed in a list, this will error when the
                # path has spaces, even while surrounded in double quotes.
                silent_Popen(
                    command_name + command_arg,
                    shell=True,
                    close_fds=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    | subprocess.CREATE_BREAKAWAY_FROM_JOB,
                )
            else:
                command = f'"{normpath}"'
                silent_Popen(
                    command,
                    shell=True,
                    close_fds=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    | subprocess.CREATE_BREAKAWAY_FROM_JOB,
                )
        else:
            if sys.platform == "darwin":
                command_name = "open"
                command_args = [str(path)]
                if file_manager:
                    # will reveal in Finder
                    command_args.append("-R")
            else:
                if file_manager:
                    command_name = "dbus-send"
                    # might not be guaranteed to launch default?
                    command_args = [
                        "--session",
                        "--dest=org.freedesktop.FileManager1",
                        "--type=method_call",
                        "/org/freedesktop/FileManager1",
                        "org.freedesktop.FileManager1.ShowItems",
                        f"array:string:file://{str(path)}",
                        "string:",
                    ]
                else:
                    command_name = "xdg-open"
                    command_args = [str(path)]
            command = shutil.which(command_name)
            if command is not None:
                silent_Popen([command] + command_args, close_fds=True)
            else:
                logger.info("Could not find command on system PATH", command=command_name)
    except Exception:
        traceback.print_exc()


class FileOpenerHelper:
    def __init__(self, filepath: str | Path):
        """Initialize the FileOpenerHelper.

        Args:
            filepath (str): The path to the file to open.
        """
        self.filepath = str(filepath)

    def set_filepath(self, filepath: str | Path):
        """Set the filepath to open.

        Args:
            filepath (str): The path to the file to open.
        """
        self.filepath = str(filepath)

    def open_file(self):
        """Open the file in the default application."""
        open_file(self.filepath)

    def open_explorer(self):
        """Open the file in the default file explorer."""
        open_file(self.filepath, file_manager=True)


class FileOpenerLabel(QLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the FileOpenerLabel.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        self.filepath: str | Path | None = None

        super().__init__(parent)

    def set_file_path(self, filepath: str | Path) -> None:
        """Set the filepath to open.

        Args:
            filepath (str): The path to the file to open.
        """
        self.filepath = filepath

    @override
    def mousePressEvent(self, ev: QMouseEvent) -> None:
        """Handle mouse press events.

        On a left click, open the file in the default file explorer.
        On a right click, show a context menu.

        Args:
            ev (QMouseEvent): The mouse press event.
        """
        if ev.button() == Qt.MouseButton.LeftButton:
            assert self.filepath is not None, "File path is not set"
            opener = FileOpenerHelper(self.filepath)
            opener.open_explorer()
        elif ev.button() == Qt.MouseButton.RightButton:
            # Show context menu
            pass
        else:
            super().mousePressEvent(ev)
