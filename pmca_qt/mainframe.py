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
            logger.debug('on_value_value_changed')
            self.sld.setValue(self.to_sld(value))
            self.valueChanged.emit(value)
        self.value.valueChanged.connect(on_value_value_changed)
        def on_sld_value_changed(sld_value):
            logger.debug('on_sld_value_changed')
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
        def on_value_changed(value):
            logger.debug('on_value_changed %f', value)
            pass
        self.slider.valueChanged.connect(on_value_changed)

    def set(self, t: PyPMCA.MODEL_TRANS_DATA):
        if self.transform==t: return
        self.transform=t
        logger.debug('set %f - %f', t.limit[0], t.limit[1])
        self.text.setText("".join('%s %f %f\n'%(x.name,x.length,x.thick) for x in t.bones))
        self.slider.setRange(*t.limit)
        self.slider.setValue((t.limit[0] + t.limit[1])/2)
        
        '''
    def changeValue(self, value):
        self.sld.valueChanged.connect(self.changeValue)
        logger.debug('slider %f', value)
        '''

    def x__init__(self, app, root, sel):
        self.app =app
        self.root=root
        self.sel =sel
        self.root.title(self.app.transform_list[self.sel].name)
        self.var =None
        self.tvar =StringVar()
        self.refbone = []
        self.refbone_index=[]
        
        self.app.transform_data.append(PyPMCA.MODEL_TRANS_DATA(name = self.app.transform_list[self.sel].name ,scale=1.0, bones=[], pos=[0.0, 0.0, 0.0], rot=[0.0, 0.0, 0.0], props={}))
        self.data = self.app.transform_data[-1]
        for i,x in enumerate(self.app.transform_list[self.sel].bones):
            self.data.bones.append(PyPMCA.BONE_TRANS_DATA(name=x.name))
    
    def CANCEL(self):
        self.app.transform_data.remove(self.data)
        self.app.refresh()
        self.root.winfo_toplevel().destroy()
        self.root.quit()
    
    def OK(self):
        self.app.transform_data[0].scale = self.data.scale * self.app.transform_data[0].scale
        for i,x in enumerate(self.app.transform_data[0].pos):
            x += self.data.pos[i]
        for i,x in enumerate(self.app.transform_data[0].rot):
            x += self.data.rot[i]
        for x in self.data.bones:
            tmp = None
            for y in self.app.transform_data[0].bones:
                if y.name==x.name:
                    tmp = y
                    break
            else:
                self.app.transform_data[0].bones.append(PyPMCA.BONE_TRANS_DATA(name=x.name))
                tmp = self.app.transform_data[0].bones[-1]
            
            tmp.length = tmp.length*x.length
            tmp.thick = tmp.thick * x.thick
            for i,y in enumerate(tmp.pos):
                y += x.pos[i]
            for i,y in enumerate(tmp.rot):
                y += x.rot[i]
        self.app.transform_data.remove(self.data)
        self.app.refresh()
        
        self.root.winfo_toplevel().destroy()
        self.root.quit()
        
        
    def change_scale(self, event):
        var = self.var.get()
        self.tvar.set('%.3f'%var)
        
        self.change_var(var)
    
    def change_spinbox(self):
        var = float(self.tvar.get())
        self.var.set(var)
        self.change_var(var)
    
    def enter_spinbox(self, event):
        try:
            var = float(self.tvar.get())
        except:
            var = self.var.get()
            return None
        
        self.tvar.set('%.3f'%var)
        self.var.set(var)
        self.change_var(var)
    
    def change_var(self, var):
        weight = self.app.transform_list[self.sel].scale
        self.data.scale = weight * var+1-weight
        
        weight = self.app.transform_list[self.sel].pos
        for i,x in enumerate(weight):
            self.data.pos[i] = x * var
        
        weight = self.app.transform_list[self.sel].rot
        for i,x in enumerate(weight):
            self.data.rot[i] = x * var

       
        for i,x in enumerate(self.app.transform_list[self.sel].bones):
            self.data.bones[i].length = x.length * var+1-x.length
            self.data.bones[i].thick = x.thick * var+1-x.thick
            for j,y in enumerate(x.pos):
                self.data.bones[i].pos[j] = y * var
            for j,y in enumerate(x.rot):
                self.data.bones[i].rot[j] = y * var
        self.app.refresh()


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

        def on_transform_select(t: PyPMCA.MODEL_TRANS_DATA):
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
