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
            return str(self.rows[index.row()])
        else:
            return None

    def setEntries(self, data):
        self.rows=data
        self.dataChanged.emit(self.get(0), self.get(-1))

    def get(self, index):
        if index<0 or index>=len(self.rows):
            return self.createIndex(0, 0, None)
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
            logger.debug('on_tree_entry %d', sel)
            self.tree_model.setEntries(entry)
            if sel>=0:
                self.tree_list.selectionModel().select(
                    self.tree_model.get(sel), QtGui.QItemSelectionModel.Select)
        parts_tree.tree_entry_observable.add(on_tree_entry)

        def on_parts_entry(entry, sel):
            logger.debug('on_parts_entry %d', sel)
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


class FloatSlider(QtGui.QWidget):
    valueChanged = QtCore.pyqtSignal(float)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        sbox=QtGui.QHBoxLayout()
        self.min=QtGui.QLabel()
        sbox.addWidget(self.min)

        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.sld.setMinimum(t.limit[0])
        #self.sld.setMaximum(t.limit[1])
        self.sld.setRange(0, 500)

        #self.sld.setGeometry(30, 40, 100, 30)
        sbox.addWidget(self.sld)

        self.max=QtGui.QLabel()
        sbox.addWidget(self.max)

        self.value=QtGui.QDoubleSpinBox()
        sbox.addWidget(self.value)

        self.setLayout(sbox)

        def on_value_value_changed(value):
            #logger.debug('on_value_value_changed')
            self.sld.setValue(self.to_sld(value))
            self.valueChanged.emit(value)
        self.value.valueChanged.connect(on_value_value_changed)
        def on_sld_value_changed(sld_value):
            #logger.debug('on_sld_value_changed')
            value=self.from_sld(sld_value)
            self.value.setValue(value)
            self.valueChanged.emit(value)
        self.sld.valueChanged.connect(on_sld_value_changed)

        self.setRange(0, 1)
        self.setValue(0.5)

    def from_sld(self, value):
        return self.range[0] + (self.range[1]-self.range[0])*(value/500.0)

    def to_sld(self, value):
        return 500.0 * (value-self.range[0])/(self.range[1]-self.range[0])

    def setRange(self, min, max):
        self.range=(min, max)
        self.min.setText(str(min))
        self.max.setText(str(max))

    def setValue(self, value):
        logger.debug('setValue %f', value)
        self.value.setValue(value)
        self.sld.setValue(self.to_sld(value))


class TransformWidget(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.build_gui()
        self.transform=None

    def build_gui(self):
        vbox=QtGui.QVBoxLayout()

        self.text=QtGui.QLabel()
        vbox.addWidget(self.text)

        vbox.addStretch(1)

        self.slider=FloatSlider()
        vbox.addWidget(self.slider)

        # button
        hbox=QtGui.QHBoxLayout()

        self.ok=QtGui.QPushButton('OK')
        hbox.addWidget(self.ok)

        self.cancel=QtGui.QPushButton('Cancel')
        hbox.addWidget(self.cancel)

        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def bind_pmca(self, transforms: PyPMCA.BodyTransform):
        self.slider.valueChanged.connect(transforms.setValue)
        self.cancel.clicked.connect(transforms.cancel)
        self.ok.clicked.connect(transforms.apply)

    def set(self):
        if self.transform==t: return
        self.transform=t
        logger.debug('set %f - %f', t.limit[0], t.limit[1])
        self.text.setText("".join('%s %f %f\n'%(x.name,x.length,x.thick) for x in t.bones))
        self.slider.setRange(*t.limit)
        self.slider.setValue((t.limit[0] + t.limit[1])/2)


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
        self.transform_widget=TransformWidget()
        hbox.addWidget(self.transform_widget)

        # set
        self.setLayout(hbox)

    def bind_pmca(self, transforms: PyPMCA.BodyTransform):
        # pmca to gui
        self.transform_model.setEntries(transforms.tmp)

        def on_transform_select(t):
            self.transform_widget.set(t)
        transforms.transform_select_observable.add(on_transform_select)

        # gui to pmca
        def transform_selected(selected, deselected):
            if(len(selected)==0):return
            range=selected[0]
            index=range.top()
            logger.debug('transform_selected %d', index)
            transforms.select_transform(index)
        self.transform_list.selectionModel().selectionChanged.connect(transform_selected)

        self.transform_widget.bind_pmca(transforms)


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
        self.add_widget('Tree', self.parts_tab, QtCore.Qt.LeftDockWidgetArea)
        # material
        self.material_tab=MaterialTab()
        self.add_widget('Color', self.material_tab, QtCore.Qt.RightDockWidgetArea)
        # transform
        self.transform_tab=TransformTab()
        self.add_widget('Transform', self.transform_tab, QtCore.Qt.RightDockWidgetArea)
        # info
        self.info_tab=InfoTab()
        self.add_widget('Info', self.info_tab, QtCore.Qt.LeftDockWidgetArea)

        # logger
        self.logger = QtGui.QPlainTextEdit()
        self.logger.setReadOnly(True)    
        self.add_widget('Logger', self.logger, QtCore.Qt.BottomDockWidgetArea)

    def add_widget(self, name: str, widget, area):
        dock = QtGui.QDockWidget(name, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)

    def bind_pmca(self, pmca: PyPMCA.PyPMCA):
        logger.info('bind_pmca')
        self.setup_menu(pmca)
        self.parts_tab.bind_pmca(pmca.parts_tree)
        self.material_tab.bind_pmca(pmca.materials)
        self.transform_tab.bind_pmca(pmca.transform)

        #
        # OpenGL
        #
        def update_gl():
            logger.debug('repaint')
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

    def setup_menu(self, pmca: PyPMCA.PyPMCA):
        menubar = self.menuBar()
        files = menubar.addMenu('ファイル')

        files.addAction(self.create_action("新規", pmca.init))

        def load():
            fname = QtGui.QFileDialog.getOpenFileName(self, 'Open CNL file', pmca.target_dir, '*.cnl')
            if fname:
                pmca.target_dir = fname.rsplit('/',1)[0]
                pmca.load_CNL_File(fname)
        files.addAction(self.create_action("読み込み", load))

        files.addSeparator()

        def save():
            fname = QtGui.QFileDialog.getSaveFileName(self, 'Save CNL file', pmca.target_dir, '*.cnl')
            if fname:
                pmca.target_dir = fname.rsplit('/',1)[0]
                pmca.save_CNL_File(fname)
        files.addAction(self.create_action("保存", save))

        def save_PMD():
            fname = QtGui.QFileDialog.getSaveFileName(self, 'Save PMD file', pmca.target_dir, '*.pmd')
            if fname:
                pmca.target_dir = fname.rsplit('/',1)[0]
                pmca.save_PMD(fname)
        files.addAction(self.create_action("モデル保存", save_PMD))

        files.addSeparator()

        def batch_assemble():
            fname = QtGui.QFileDialog.getOpenFileNames(self, 'Open CNL file', pmca.target_dir, '*.cnl')
            if fname and len(fname)>0:
                pmca.target_dir = fname[0].rsplit('/',1)[0]
                pmca.batch_assemble(fname)
        files.addAction(self.create_action("一括組立て", batch_assemble))

        files.addSeparator()

        def savecheck_PMD():
            errors=pmca.savecheck_PMD()
            logger.debug(errors)
        files.addAction(self.create_action("PMDフォーマットチェック", savecheck_PMD))

        def check_PMD():
            errors=pmca.check_PMD()
            logger.debug(errors)
        files.addAction(self.create_action("PMD概要確認", check_PMD))

        def propcheck_PMD():
            errors=pmca.propcheck_PMD()
            logger.debug(errors)
        files.addAction(self.create_action("PMD詳細確認", propcheck_PMD))

        files.addSeparator()
        files.addAction(self.create_action('exit', QtGui.qApp.quit))
        
        editing = menubar.addMenu("編集")
        editing.addAction(self.create_action("体型調整を初期化", pmca.transform.clear))
        editing.addAction(self.create_action("材質をランダム選択", pmca.materials.random))
        editing.addAction(self.create_action("PMCA設定", self.setting_dialog))
        
    def create_action(self, label, callback):
        action = QtGui.QAction(label, self)        
        action.triggered.connect(callback)
        return action

    def setting_dialog(self):
        pass
