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

    def bind_pmca(self, parts_tree: PyPMCA.PartsTree):
        # pmca to gui
        def on_tree_entry(entry, sel):
            print('qt:on_tree_entry', entry, sel)
            self.tree_model.setEntries(entry)
            if sel>=0:
                self.tree_list.selectionModel().select(
                    self.tree_model.get(sel), QtGui.QItemSelectionModel.Select)
        parts_tree.tree_entry_observable.add(on_tree_entry)

        def on_parts_entry(entry, sel):
            print('qt:on_parts_entry', entry, sel)
            self.parts_model.setEntries(entry)
            if sel>=0:
                self.parts_list.selectionModel().select(
                    self.tree_model.get(sel), QtGui.QItemSelectionModel.Select)
        parts_tree.parts_entry_observable.add(on_parts_entry)

        # gui to pmca
        def tree_selected(selected, deselected):
            print('qt:tree_selected')
            if(len(selected)==0):return
            range=selected[0]
            index=range.top()
            print('qt:tree_selected', index)
            parts_tree.select_node(index)
        self.tree_list.selectionModel().selectionChanged.connect(tree_selected)

        def parts_selected(selected, deselected):
            print('qt:parts_selected')
            if(len(selected)==0):return
            range=selected[0]
            index=range.top()
            print('qt:parts_selected', index)
            parts_tree.select_part(index)
        self.parts_list.selectionModel().selectionChanged.connect(parts_selected)


class MaterialTab(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        hbox = QtGui.QHBoxLayout()
        # left
        self.material_model=ListModel()
        self.material_list = QtGui.QListView()
        self.material_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.material_list.setModel(self.material_model)
        hbox.addWidget(self.material_list)
        # right
        self.color_model=ListModel()
        self.color_list=QtGui.QListView()
        self.color_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.color_list.setModel(self.color_model)
        hbox.addWidget(self.color_list)
        # set
        self.setLayout(hbox)

    def bind_pmca(self, materials: PyPMCA.MaterialSelector):
        # pmca to gui
        def on_material_entry(entry, sel):
            print('qt:on_material_entry', entry, sel)
            self.material_model.setEntries(entry)
            if sel>=0:
                self.material_list.selectionModel().select(
                    self.material_model.get(sel), QtGui.QItemSelectionModel.Select)
        materials.material_entry_observable.add(on_material_entry)

        def on_color_entry(entry, sel):
            print('qt:on_color_entry', entry, sel)
            self.color_model.setEntries(entry)
            if sel>=0:
                self.color_list.selectionModel().select(
                    self.color_model.get(sel), QtGui.QItemSelectionModel.Select)
        materials.color_entry_observable.add(on_color_entry)

        # gui to pmca
        def material_selected(selected, deselected):
            print('qt:material_selected')
            if(len(selected)==0):return
            range=selected[0]
            index=range.top()
            print('qt:material_selected', index)
            materials.select_material(index)
        self.material_list.selectionModel().selectionChanged.connect(material_selected)

        def color_selected(selected, deselected):
            print('qt:color_selected')
            if(len(selected)==0):return
            range=selected[0]
            index=range.top()
            print('qt:color_selected', index)
            materials.select_color(index)
        self.color_list.selectionModel().selectionChanged.connect(color_selected)


class TransformTab(QtGui.QWidget):
    def __init__(self):
        super().__init__()


class InfoTab(QtGui.QWidget):
    def __init__(self):
        super().__init__()


class MainFrame(QtGui.QMainWindow):   
    def __init__(self, glcontroller):
        super().__init__()
        self.statusBar().showMessage('Ready')
        self.setWindowTitle(PyPMCA.APP_NAME)

        # centeral
        self.main=pmca_qt.GLFrame(glcontroller)
        self.setCentralWidget(self.main)

        # parts
        self.parts_tab=PartsTab()
        self.add_widget('Tree', self.parts_tab)
        # material
        self.material_tab=MaterialTab()
        self.add_widget('Color', self.material_tab)
        # transform
        self.transform_tab=TransformTab()
        self.add_widget('Transform', self.transform_tab)
        # info
        self.info_tab=InfoTab()
        self.add_widget('Info', self.info_tab)

    def add_widget(self, name: str, widget):
        dock = QtGui.QDockWidget(name, self)
        dock.setWidget(widget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    def bind_pmca(self, pmca):
        self.parts_tab.bind_pmca(pmca.parts_tree)
        self.material_tab.bind_pmca(pmca.materials)
