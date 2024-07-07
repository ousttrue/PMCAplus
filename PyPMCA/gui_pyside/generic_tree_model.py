from typing import Generic, TypeVar, Callable, cast
from PySide6 import QtCore


T = TypeVar("T")


class GenericTreeModel(QtCore.QAbstractItemModel, Generic[T]):
    def __init__(
        self,
        get_parent: Callable[[T], T | None],
        get_child_count: Callable[[T | None], int],
        get_child: Callable[[T | None, int], T],
        headers: list[str],
        column_from_item: Callable[[T, int], str],
    ):
        super().__init__()
        self.headers = headers
        self.get_parent = get_parent
        self.get_child_count = get_child_count
        self.get_child = get_child
        self.column_from_item = column_from_item

    def columnCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> int:  # type: ignore
        return len(self.headers)

    def data(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex, role: QtCore.Qt.ItemDataRole) -> str | None:  # type: ignore
        if role == QtCore.Qt.DisplayRole:  # type: ignore
            if index.isValid():
                item: T = index.internalPointer()  # type: ignore
                return self.column_from_item(item, index.column())

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole) -> str | None:  # type: ignore
        match orientation, role:
            case QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole:  # type: ignore
                return self.headers[section]
            case _:
                pass

    def index(  # type: ignore
        self,
        row: int,
        column: int,
        parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> QtCore.QModelIndex:
        if parent.isValid():
            parentItem: T = parent.internalPointer()  # type: ignore
            childItem = self.get_child(parentItem, row)
            return self.createIndex(row, column, childItem)
        else:
            childItem = self.get_child(None, row)
            return self.createIndex(row, column, childItem)

    def parent(  # type: ignore
        self,
        child: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> QtCore.QModelIndex:
        if child.isValid():
            childItem = cast(T, child.internalPointer())  # type: ignore
            # row, parentItem = self.get_parent(childItem)
            if childItem:
                parentItem = self.get_parent(childItem)
                if parentItem:
                    return self.createIndex(0, 0, parentItem)

        return QtCore.QModelIndex()

    def rowCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> int:  # type: ignore
        if parent.isValid():
            parentItem: T = parent.internalPointer()  # type: ignore
            return self.get_child_count(parentItem)
        else:
            return self.get_child_count(None)


class GenericListModel(GenericTreeModel[T]):
    def __init__(
        self,
        items: list[T],
        headers: list[str],
        get_col: Callable[[T, int], str],
    ) -> None:
        super().__init__(
            lambda x: None,
            lambda x: 0 if x else len(items),
            lambda x, row: items[row],
            headers,
            get_col,
        )
        self.parts_list = items

    def index_from_item(self, target: T) -> QtCore.QModelIndex:
        for i, parts in enumerate(self.parts_list):
            if parts == target:
                return self.createIndex(i, 0, parts)

        return QtCore.QModelIndex()
