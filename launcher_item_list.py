# coding: utf-8
from typing import Iterable, List, Optional

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton, QScrollArea, QVBoxLayout, QWidget

from launcher_item import LauncherItem

__all__ = ["LauncherItemList"]


class LauncherItemList(QScrollArea):
    _index: int

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        w: QWidget = QWidget(self)
        self.setWidget(w)
        self.setWidgetResizable(True)
        self._layout: QVBoxLayout = QVBoxLayout(w)
        self._button_add: QPushButton = QPushButton(self.tr("Add"), w)
        self._button_add.clicked.connect(self.on_add_clicked)
        self._layout.addWidget(self._button_add)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._items: List[LauncherItem] = []

    def __getitem__(self, index: int) -> LauncherItem:
        return self._items[index]

    def __len__(self) -> int:
        return len(self._items)

    def on_add_clicked(self) -> None:
        self.add_item()

    def add_item(
        self,
        alias: str = "",
        executable: str = "",
        arguments: Iterable[str] = (),
    ) -> None:
        self._items.append(
            LauncherItem(
                alias=alias,
                executable=executable,
                arguments=arguments,
                parent=self,
            )
        )
        self._layout.insertWidget(len(self._items) - 1, self._items[-1])
        self._items[-1].deleted.connect(self.delete_item)

    def delete_item(self, index: int) -> None:
        item: LauncherItem
        for item in self._items:
            if item.index == index:
                self._layout.removeWidget(item)
                self._items.remove(item)
