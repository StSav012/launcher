# coding: utf-8
import sys
from pathlib import Path
from typing import Optional

import pathvalidate
from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
    QWidget,
)

__all__ = ['FilePathEntry']


class FilePathEntry(QWidget):
    changed: Signal = Signal(bool, name='changed')

    def __init__(self, initial_file_path: str = '', parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._path: Optional[Path] = None

        self.setLayout(QHBoxLayout())

        self._text: QLineEdit = QLineEdit(self)
        self.layout().addWidget(self._text)

        self._status: QLabel = QLabel(self)
        self.layout().addWidget(self._status)

        self._browse_button: QPushButton = QPushButton(self.tr('Browse…'), self)
        self._browse_button.clicked.connect(self.on_browse_button_clicked)
        self.layout().addWidget(self._browse_button)

        self._text.textChanged.connect(self.on_text_changed)
        self._text.setText(initial_file_path)

        self.layout().setStretch(1, 0)
        self.layout().setStretch(2, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

    @property
    def valid(self) -> bool:
        return self._path is not None

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, new_path: Optional[Path]) -> None:
        self._path = new_path
        self.changed.emit(self.valid)

    def on_text_changed(self, text: str) -> None:
        """ display an icon showing whether the entered file name is acceptable """

        self._text.setToolTip(text)

        if not text:
            self._status.clear()
            self.path = None
            return

        try:
            path: Path = Path(text).resolve()
        except OSError:
            self._status.setPixmap(self.style()
                                   .standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
                                   .pixmap(self._text.height()))
            self.path = None
            return
        if path.is_dir():
            self._status.setPixmap(self.style()
                                   .standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
                                   .pixmap(self._text.height()))
            self.path = None
            return
        if not path.exists():
            self._status.setPixmap(self.style()
                                   .standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
                                   .pixmap(self._text.height()))
            self.path = path
            return
        try:
            pathvalidate.validate_filepath(path, platform='auto')
        except pathvalidate.error.ValidationError:
            self._status.setPixmap(self.style()
                                   .standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
                                   .pixmap(self._text.height()))
            self.path = None
        else:
            self._status.clear()
            self.path = path

    def on_browse_button_clicked(self) -> None:
        new_file_name: str
        new_file_name, _ = QFileDialog.getOpenFileName(
            self, self.tr('Pick Executable'),
            str(self.path or ''),
            self.tr('Microsoft Windows Executable') + ' (*.exe)' if sys.platform.startswith('win') else '')
        if new_file_name:
            self._text.setText(new_file_name)
