import sys
from PyQt4 import QtGui, QtCore
import PyPMCA
import pmca_qt


class ListModel(QtCore.QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.rows=[]

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.rows)

    def data(self, index, role):
        if not index.isValid():
            return None

        if index.row() >= len(self.rows):
            return None

        if role == QtCore.Qt.DisplayRole:
            return self.rows[index.row()]
        else:
            return None

    def setEntries(self, data):
        self.rows=data
        self.dataChanged.emit(self.get(0), self.get(-1))

    def get(self, index):
        if index<0:
            return self.createIndex(len(self.rows)+index, 0, self.rows[index])
        else:
            return self.createIndex(index, 0, self.rows[index])

class PartsTab(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        hbox = QtGui.QHBoxLayout()
        # left
        self.tree_model=ListModel()
        self.tree_list = QtGui.QListView()
        self.tree_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tree_list.setModel(self.tree_model)
        hbox.addWidget(self.tree_list)
        # right
        self.parts_model=ListModel()
        self.parts_list=QtGui.QListView()
        self.parts_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.parts_list.setModel(self.parts_model)
        hbox.addWidget(self.parts_list)
        # set
        self.setLayout(hbox)

    def bind_pmca(self, pmca):
        def on_tree_entry(entry, sel):
            self.tree_model.setEntries(entry)
            self.tree_list.selectionModel().select(self.tree_model.get(sel), QtGui.QItemSelectionModel.Select)
        pmca.parts_tree.tree_entry_observable.add(on_tree_entry)

        def on_parts_entry(entry, sel):
            self.parts_model.setEntries(entry)
        pmca.parts_tree.parts_entry_observable.add(on_parts_entry)


class MaterialTab(QtGui.QWidget):
    def __init(self):
        super().__init()


class TransformTab(QtGui.QWidget):
    def __init(self):
        super().__init()


class InfoTab(QtGui.QWidget):
    def __init(self):
        super().__init()


class MainWidget(QtGui.QWidget):
    def __init__(self, glcontroller):
        super().__init__()

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(pmca_qt.GLFrame(glcontroller))
        vbox.addWidget(self.tab_ui())
        vbox.addLayout(self.lower_layout())

        self.setLayout(vbox)

    def tab_ui(self):
        tab = QtGui.QTabWidget()
        self.parts_tab=PartsTab()
        tab.addTab(self.parts_tab, 'Parts')
        tab.addTab(MaterialTab(), 'Material')
        tab.addTab(TransformTab(), 'Transform')
        tab.addTab(InfoTab(), 'Info')
        return tab

    def lower_layout(self):
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        quitButton = QtGui.QPushButton("QUIT")
        hbox.addWidget(quitButton)
        return hbox

    def bind_pmca(self, pmca):
        self.parts_tab.bind_pmca(pmca)


class MainFrame(QtGui.QMainWindow):   
    def __init__(self, glcontroller):
        super().__init__()
        self.statusBar().showMessage('Ready')
        self.setWindowTitle(PyPMCA.APP_NAME)
        self.main=MainWidget(glcontroller)
        self.setCentralWidget(self.main)

    def bind_pmca(self, pmca):
        self.main.bind_pmca(pmca)
