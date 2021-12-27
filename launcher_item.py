# coding: utf-8
import subprocess
from typing import Final, Iterable, Optional, Tuple

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QAction, QContextMenuEvent, QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMenu, QMessageBox, QStyle, QToolButton, QWidget

from edit_dialog import EditDialog

__all__ = ['LauncherItem']


class LauncherItem(QWidget):
    _count: int = 0

    deleted: Signal = Signal(int, name='deleted')

    def __init__(self, alias: str, executable: str = '', arguments: Iterable[str] = (),
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._icon: QLabel = QLabel(self)
        self._alias_label: QLabel = QLabel(self)
        self._launch_button: QToolButton = QToolButton(self)
        self._menu: QMenu = QMenu(self)
        self._edit_action: QAction = QAction(self.tr('Edit'), self)
        self._delete_action: QAction = QAction(self.tr('Delete'), self)
        self._executable: str = executable
        self._arguments: Tuple[str] = tuple(arguments)

        self._menu.addActions((self._edit_action, self._delete_action))

        layout: QHBoxLayout = QHBoxLayout(self)
        layout.addWidget(self._icon)
        layout.addWidget(self._alias_label, 1)
        layout.addWidget(self._launch_button)

        if not alias or not executable:
            self.on_edit()
        else:
            self._alias_label.setText(alias)

        self._icon.setPixmap(self.style()
                             .standardIcon(QStyle.StandardPixmap.SP_CommandLink)
                             .pixmap(self._alias_label.height()))
        self._launch_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight))
        self._launch_button.setText(self.tr('Launch'))

        self._launch_button.clicked.connect(self.on_launch)
        self._edit_action.triggered.connect(self.on_edit)
        self._delete_action.triggered.connect(self.on_delete)

        self._index: Final[int] = LauncherItem._count
        LauncherItem._count += 1

    @property
    def index(self) -> int:
        return self._index

    @property
    def alias(self) -> str:
        return self._alias_label.text()

    @property
    def executable(self) -> str:
        return self._executable

    @property
    def arguments(self) -> Tuple[str]:
        return self._arguments

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton:
            event.accept()
            return
        self.on_launch()
        event.accept()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        self._menu.exec(event.globalPos())
        event.accept()

    def leaveEvent(self, event: QEvent) -> None:
        self.setEnabled(True)
        return super().leaveEvent(event)

    def on_launch(self) -> None:
        self.setEnabled(False)
        try:
            subprocess.Popen(executable=self._executable, args=self._arguments)
        except FileNotFoundError:
            QMessageBox.warning(self, self.tr('Error'), self.tr('File not found'))
        except PermissionError as ex:
            QMessageBox.warning(self, self.tr('Error'), ex.strerror)

    def on_edit(self) -> None:
        dialog: EditDialog = EditDialog(self._alias_label.text(), self._executable, args=self._arguments, parent=self)
        dialog.exec()
        self._alias_label.setText(dialog.alias)
        self._executable = dialog.executable
        self._arguments = list(dialog.args)

    def on_delete(self) -> None:
        self.hide()
        self.deleted.emit(self.index)
