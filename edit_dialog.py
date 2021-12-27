# coding: utf-8
import os
from typing import Iterable, List, Optional

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QTextEdit, QWidget

from file_path_entry import FilePathEntry

__all__ = ['EditDialog']


class EditDialog(QDialog):
    def __init__(self, alias: str, exe: str, args: Iterable[str] = (), parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.alias: str = alias
        self.executable: str = exe
        self.args: List[str] = list(args)

        self.setWindowTitle(self.tr('Edit'))

        layout: QFormLayout = QFormLayout(self)
        self._alias_entry: QLineEdit = QLineEdit(self)
        self._alias_entry.setText(alias)
        self._alias_entry.textChanged.connect(self.on_alias_changed)
        layout.addRow(self.tr('Alias:'), self._alias_entry)
        self._exe_entry: FilePathEntry = FilePathEntry(str(self.executable), self)
        self._exe_entry.changed.connect(self.on_exe_changed)
        layout.addRow(self.tr('Executable:'), self._exe_entry)
        self._args_entry: QTextEdit = QTextEdit('<p>' + '</p><p>'.join(self.args) + '</p>', self)
        self._args_entry.setAcceptRichText(False)
        self._args_entry.setFontFamily('monospace')
        layout.addRow(self.tr('Arguments <i>(one per line)</i>:'), self._args_entry)

        self._buttons: QDialogButtonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                                           | QDialogButtonBox.StandardButton.Cancel, self)
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(self._exe_entry.valid and bool(alias))
        layout.addWidget(self._buttons)
        self._buttons.rejected.connect(self.reject)
        self._buttons.accepted.connect(self.accept)

    def __repr__(self) -> str:
        lines: List[str] = [
            f'Alias:     \t{self.alias}',
            f'Executable:\t{self.executable}'
        ]
        if self.args:
            lines += ['Arguments:'] + [f'    {a}' for a in self.args]
        else:
            lines += ['No arguments']
        return os.linesep.join(lines)

    def accept(self) -> None:
        self.alias = self._alias_entry.text()
        self.executable = str(self._exe_entry.path)
        self.args = self._args_entry.toPlainText().splitlines()
        super().accept()

    def on_alias_changed(self, new_alias: str) -> None:
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(bool(new_alias) and self._exe_entry.valid)

    def on_exe_changed(self, valid: bool) -> None:
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(valid and bool(self._alias_entry.text()))
