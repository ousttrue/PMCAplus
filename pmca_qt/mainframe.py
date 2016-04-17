import sys
import os
sys.path.append(os.getcwd()+'/glglue')
import glglue.sample
import glglue.qgl

from PyQt4 import QtGui, QtCore
import PyPMCA
import pmca_qt

from logging import getLogger
logger = getLogger(__name__)


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
        if len(self.rows)==0:
            return self.createIndex(0, 0, None)
        elif index<0:
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
            logger.debug('on_tree_entry %s, %d', entry, sel)
            self.tree_model.setEntries(entry)
            if sel>=0:
                self.tree_list.selectionModel().select(
                    self.tree_model.get(sel), QtGui.QItemSelectionModel.Select)
        parts_tree.tree_entry_observable.add(on_tree_entry)

        def on_parts_entry(entry, sel):
            logger.debug('on_parts_entry %s, %d', entry, sel)
            self.parts_model.setEntries(entry)
            if sel>=0:
                self.parts_list.selectionModel().select(
                    self.tree_model.get(sel), QtGui.QItemSelectionModel.Select)
        parts_tree.parts_entry_observable.add(on_parts_entry)

        # gui to pmca
        def tree_selected(selected, deselected):
            if(len(selected)==0):return
            range=selected[0]
            index=range.top()
            logger.debug('tree_selected %d', index)
            parts_tree.select_node(index)
        self.tree_list.selectionModel().selectionChanged.connect(tree_selected)

        def parts_selected(selected, deselected):
            if(len(selected)==0):return
            range=selected[0]
            index=range.top()
            logger.debug('parts_selected %d', index)
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
            logger.debug('on_material_entry %s, %d', entry, sel)
            self.material_model.setEntries(entry)
            if sel>=0:
                self.material_list.selectionModel().select(
                    self.material_model.get(sel), QtGui.QItemSelectionModel.Select)
        materials.material_entry_observable.add(on_material_entry)

        def on_color_entry(entry, sel):
            logger.debug('on_color_entry %s, %d', entry, sel)
            self.color_model.setEntries(entry)
            if sel>=0:
                self.color_list.selectionModel().select(
                    self.color_model.get(sel), QtGui.QItemSelectionModel.Select)
        materials.color_entry_observable.add(on_color_entry)

        # gui to pmca
        def material_selected(selected, deselected):
            if(len(selected)==0):return
            range=selected[0]
            index=range.top()
            logger.debug('material_selected %d', index)
            materials.select_material(index)
        self.material_list.selectionModel().selectionChanged.connect(material_selected)

        def color_selected(selected, deselected):
            if(len(selected)==0):return
            range=selected[0]
            index=range.top()
            logger.debug('color_selected %d', index)
            materials.select_color(index)
        self.color_list.selectionModel().selectionChanged.connect(color_selected)


class TransformWidget(QtGui.QWidget):
    def __init__(self):
        super().__init__()


class TransformTab(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        hbox = QtGui.QHBoxLayout()
        # left
        self.transform_model=ListModel()
        self.transform_list = QtGui.QListView()
        self.transform_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.transform_list.setModel(self.transform_model)
        hbox.addWidget(self.transform_list)
        # right
        hbox.addWidget(TransformWidget())
        # set
        self.setLayout(hbox)

    def bind_pmca(self, transforms: PyPMCA.BodyTransform):
        # pmca to gui
        self.transform_model.setEntries(transforms.tmp)

        # gui to pmca
        def transform_selected(selected, deselected):
            if(len(selected)==0):return
            range=selected[0]
            index=range.top()
            logger.debug('transform_selected %d', index)
            #transforms.select_body(None, index)
        self.transform_list.selectionModel().selectionChanged.connect(transform_selected)


class InfoTab(QtGui.QWidget):
    def __init__(self):
        super().__init__()


class MainFrame(QtGui.QMainWindow):   
    def __init__(self, glcontroller):
        super().__init__()
        self.statusBar().showMessage('Ready')
        self.setWindowTitle(PyPMCA.APP_NAME)

        # OpenGL
        self.glframe=glglue.qgl.Widget(self, glcontroller)
        self.setCentralWidget(self.glframe)

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

        # logger
        self.logger = QtGui.QPlainTextEdit()
        self.logger.setReadOnly(True)    
        self.add_widget('Logger', self.logger, QtCore.Qt.BottomDockWidgetArea)

    def add_widget(self, name: str, widget, area=QtCore.Qt.RightDockWidgetArea):
        dock = QtGui.QDockWidget(name, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)

    def bind_pmca(self, pmca):
        logger.info('bind_pmca')
        self.parts_tab.bind_pmca(pmca.parts_tree)
        self.material_tab.bind_pmca(pmca.materials)
        self.transform_tab.bind_pmca(pmca.transform)

        #
        # OpenGL
        #
        def update_gl():
            self.glframe.repaint()
        pmca.model_update_observable.add(update_gl)

        #
        # 更新タイマー
        #
        self.timer = QtCore.QTimer()
        def timer_update():
            pmca.update()
        self.timer.timeout.connect(timer_update)
        self.timer.start(33)
