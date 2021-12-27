# coding: utf-8
import sys

from PySide6.QtCore import QByteArray, QPoint, QRect, QSettings
from PySide6.QtGui import QCloseEvent, QIcon, QScreen
from PySide6.QtWidgets import QApplication, QMainWindow

from launcher_item import LauncherItem
from launcher_item_list import LauncherItemList


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr('Launcher'))
        self.setWindowIcon(QIcon('icon.svg'))

        self.settings: QSettings = QSettings('SavSoft', 'Launcher', self)

        self.list: LauncherItemList = LauncherItemList(self)
        self.setCentralWidget(self.list)

        self.load_settings()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.save_settings()
        event.accept()

    def load_settings(self) -> None:
        items_count: int = self.settings.beginReadArray('items')
        index: int
        for index in range(items_count):
            self.settings.setArrayIndex(index)
            self.list.add_item(alias=self.settings.value('alias', '', str),
                               executable=str(self.settings.value('executable', '')),
                               arguments=self.settings.value('arguments', '', str).split('\n'))
        self.settings.endArray()

        self.settings.beginGroup('window')
        # Fallback: Center the window
        desktop: QScreen = QApplication.screens()[0]
        window_frame: QRect = self.frameGeometry()
        desktop_center: QPoint = desktop.availableGeometry().center()
        window_frame.moveCenter(desktop_center)
        self.move(window_frame.topLeft())

        # noinspection PyTypeChecker
        self.restoreGeometry(self.settings.value('geometry', QByteArray()))
        # noinspection PyTypeChecker
        self.restoreState(self.settings.value('state', QByteArray()))
        self.settings.endGroup()

    def save_settings(self) -> None:
        self.settings.beginWriteArray('items')
        index: int
        item: LauncherItem
        for index, item in enumerate(self.list):
            self.settings.setArrayIndex(index)
            self.settings.setValue('alias', self.list[index].alias)
            self.settings.setValue('executable', self.list[index].executable)
            self.settings.setValue('arguments', '\n'.join(self.list[index].arguments))
        self.settings.endArray()

        self.settings.beginGroup('window')
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('state', self.saveState())
        self.settings.endGroup()
        self.settings.sync()


if __name__ == '__main__':
    app: QApplication = QApplication(sys.argv)
    window: Window = Window()
    window.show()
    app.exec()
