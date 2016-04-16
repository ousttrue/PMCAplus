# coding: utf-8
import PMCA
import PMCA_dialogs
from PyPMCA.pmd import INFO, BONE, Observable
from tkinter import *
from logging import getLogger
logger = getLogger(__name__)


def load_translist(fp, trans_list):
	trans_list.append(MODEL_TRANS_DATA(bones=[]))
	
	line = fp.readline()
	mode = 0
	
	while line:
		line = line.rstrip('\n').replace('\t',' ').split(' ', 1)
		if line[0]=='':
			pass
		if line[0][:1]=='#':
			pass
		elif line[0]=='NEXT':
			trans_list.append(MODEL_TRANS_DATA(scale=0.0, bones=[]))
			mode = 0
		
		elif len(line)<2:
			pass
		
		elif line[0]=='[ENTRY]':
			trans_list[-1].bones.append(BONE_TRANS_DATA(name = line[1], length=0.0, thick=0.0, props = {}))
			mode = 1
		elif line[0]=='[name]':
			if mode == 0:
				trans_list[-1].name = line[1]
		elif line[0]=='[scale]':
			if mode == 0:
				trans_list[-1].scale = float(line[1])
			elif mode == 1:
				trans_list[-1].bones[-1].length = float(line[1])
				trans_list[-1].bones[-1].thick = float(line[1])
		elif line[0]=='[length]':
			if mode == 1:
				trans_list[-1].bones[-1].length = float(line[1])
		elif line[0]=='[thick]':
			if mode == 1:
				trans_list[-1].bones[-1].thick = float(line[1])
		elif line[0]=='[pos]':
			tmp = line[1].split(' ')
			if mode == 0:
				trans_list[-1].pos = [float(tmp[0]),float(tmp[1]),float(tmp[2])]
			elif mode == 1:
				trans_list[-1].bones[-1].pos = [float(tmp[0]),float(tmp[1]),float(tmp[2])]
		elif line[0]=='[range]':
			tmp = line[1].split(' ')
			trans_list[-1].limit = [float(tmp[0]),float(tmp[1])]
		elif line[0]=='[default]':
			trans_list[-1].default = float(line[1])
		elif line[0][:1] == '[' and line[0][-1:] == ']':
			if line[0][1:-1] in trans_list[-1].props:
				trans_list[-1].props[line[0][1:-1]].append(line[1])
			else:
				trans_list[-1].props[line[0][1:-1]] = [line[1]]
		line = fp.readline()
	'''
	mats_list.append(mats_list[-1])
	if mats_list[-1].entries[-1].__class__.__name__ == 'MATS_ENTRY':
		mats_list[-1].entries.append(mats_list[-1].entries[-1])
	'''
	
	return trans_list


class MODEL_TRANS_DATA:
	def __init__(self, name='', scale=1.0, pos=[0.0,0.0,0.0], rot=[0.0,0.0,0.0], bones=[], limit=[0.0,2.0], default=1.0, gamma=1.0, props={}):
		self.name  = name
		self.scale = scale
		self.pos   = pos
		self.rot   = rot
		self.bones = bones
		self.limit = limit
		self.default = default
		self.gamma = gamma
		self.props=props
	
	def list_to_text(self):
		lines=[]
		#lines.append('[Name] %s'%(self.name))
		lines.append('[Scale] %f'%(self.scale))
		lines.append('[Pos] %f %f %f'%(self.pos[0],self.pos[1],self.pos[2]))
		lines.append('[Rot] %f %f %f'%(self.rot[0],self.rot[1],self.rot[2]))
		lines.append('BONES')
		for x in self.bones:
			lines.append('[Name] %s'%(x.name))
			lines.append('[Length] %f'%(x.length))
			lines.append('[Thick] %f'%(x.thick))
			lines.append('[Pos] %f %f %f'%(x.pos[0], x.pos[1], x.pos[2]))
			lines.append('[Rot] %f %f %f'%(x.rot[0], x.rot[1], x.rot[2]))
			lines.append('NEXT')
		lines.pop()
		
		return lines
	
	def text_to_list(self, lines):
		tmp = ['','',None]
		i=0
		try:
			while lines[i] != 'TRANSFORM':
				i+=1
		except:
			return None
		
		i+=1
		for j,x in enumerate(lines[i:]):
			x = x.split(' ')
			if x[0] == '[Name]':
				self.name = x[1]
			elif x[0] == '[Scale]':
				self.scale = float(x[1])
			elif x[0] == '[Pos]':
				self.pos[0] = float(x[1])
				self.pos[1] = float(x[2])
				self.pos[2] = float(x[3])
			elif x[0] == '[Rot]':
				self.rot[0] = float(x[1])
				self.rot[1] = float(x[2])
				self.rot[2] = float(x[3])
			elif x[0] == 'BONES':
				break
		self.bones = []
		self.bones.append(BONE_TRANS_DATA())
		for x in lines[i+j:]:
			x = x.split(' ')
			if x[0] == '[Name]':
				self.bones[-1].name = x[1]
			elif x[0] == '[Length]':
				self.bones[-1].length = float(x[1])
			elif x[0] == '[Thick]':
				self.bones[-1].thick = float(x[1])
			elif x[0] == '[Pos]':
				self.bones[-1].pos[0] = float(x[1])
				self.bones[-1].pos[1] = float(x[2])
				self.bones[-1].pos[2] = float(x[3])
			elif x[0] == '[Rot]':
				self.bones[-1].rot[0] = float(x[1])
				self.bones[-1].rot[1] = float(x[2])
				self.bones[-1].rot[2] = float(x[3])
			elif x[0] == 'NEXT':
				if self.bones[-1].name != '':
					self.bones.append(BONE_TRANS_DATA())
				
		
class BONE_TRANS_DATA:
	def __init__(self, name='', length=1.0, thick=1.0, pos=[0.0,0.0,0.0], rot=[0.0,0.0,0.0], props={}):
		self.name  = name
		self.length= length
		self.thick = thick
		self.pos   = pos
		self.rot   = rot
		self.props=props


class BodyTransform:
    def __init__(self):
        self.transform_data = []
        self.transform_list = []
        self.transform_data=[MODEL_TRANS_DATA(scale=1.0, bones=[], props={})]
        self.transform_observable=Observable()

    def refresh(self):
        self.transform_observable.notify()

    def load_transformlist(self, fp):
        self.transform_list = load_translist(fp, self.transform_list)
        self.tmp = []
        for x in self.transform_list:
            self.tmp.append(x.name)

    def clear(self):
        self.transform_data = [MODEL_TRANS_DATA(scale=1.0, pos=[0.0, 0.0, 0.0], rot=[0.0, 0.0, 0.0], bones=[], props={})]
        self.transform_observable.notify()

    def load_CNL_lines(self, lines):
        self.transform_data[0].text_to_list(lines)

    def select_body(self, frame, sel):
        buff=''
        
        for x in self.transform_list[sel].bones:
            buff += '%s %f %f\n'%(x.name,x.length,x.thick)
        
        t = self.transform_list[sel]
        
        root = Toplevel()
        root.fancs = PMCA_dialogs.SCALE_DIALOG_FANC(self,root, sel)
        
        root.fancs.var = DoubleVar()
        root.fancs.var.set(t.default)
        root.fancs.tvar.set('%.3f'%t.default)
        
        root.transient(frame)
        root.frame1 = Frame(root)
        root.frame2 = Frame(root)
        
        Label(root, text = buff).grid(row=0, padx=10, pady=5)
        
        root.frame1.spinbox = Spinbox(root.frame1, from_=-100, to=100, increment=0.02, format = '%.3f', textvariable=root.fancs.tvar, width=5, command=root.fancs.change_spinbox)
        root.frame1.spinbox.pack(side="right", padx=5)
        root.frame1.spinbox.bind('<Return>', root.fancs.enter_spinbox)
        
        Scale(root.frame1, orient = 'h',from_ = t.limit[0], to = t.limit[1], 
              variable = root.fancs.var , 
              resolution = -1,
              length = 256, 
              command=root.fancs.change_scale).pack(side="left", padx=5)
        root.frame1.grid(row=1, padx=10, pady=5)
        
        Button(root.frame2, text = 'OK', command = root.fancs.OK).pack(side="right", padx=5)
        Button(root.frame2, text = 'Cancel', command = root.fancs.CANCEL).pack(side="left", padx=5)
        root.frame2.grid(row=2, sticky="e", padx=10, pady=5)
        root.mainloop()

    def update(self):
        info_data = PMCA.getInfo(0)
        info = INFO(info_data)
            
        tmpbone = []
        for i in range(info_data["bone_count"]):
            tmp = PMCA.getBone(0, i)
            tmpbone.append(BONE(tmp['name'], tmp['name_eng'], tmp['parent'], tmp['tail'], tmp['type'], tmp['IK'], tmp['loc']))
        refbone = None
        refbone_index = None
        for i,x in enumerate(tmpbone):
            if x.name == "右足首":
                refbone = x
                refbone_index = i
                break
            
        for y in self.transform_data:
            PMCA.Resize_Model(0,y.scale)
            for x in y.bones:
                PMCA.Resize_Bone(0, x.name.encode('cp932','replace'), x.length, x.thick)
                PMCA.Move_Bone(0, x.name.encode('cp932','replace'),x.pos[0], x.pos[1], x.pos[2])
            
        if refbone!=None:
            newbone=None
            tmp = PMCA.getBone(0, refbone_index)
            newbone = BONE(tmp['name'], tmp['name_eng'], tmp['parent'], tmp['tail'], tmp['type'], tmp['IK'], tmp['loc'])
                
            dy = refbone.loc[1] - newbone.loc[1]
            for x in tmpbone:
                i = x.parent
                count = 0
                while i < info_data["bone_count"] and count < info_data["bone_count"]:
                    if tmpbone[i].name == 'センター':
                        PMCA.Move_Bone(0, x.name.encode('cp932','replace'), 0, dy, 0)
                        break
                    i=tmpbone[i].parent
                    count += 1
                
            PMCA.Move_Bone(0, 'センター'.encode('cp932','replace'), 0, dy, 0)
            PMCA.Move_Bone(0, '+センター'.encode('cp932','replace'), 0, -dy, 0)
            
        for y in self.transform_data:
            PMCA.Move_Model(0,y.pos[0],y.pos[1],y.pos[2])
            
        PMCA.Update_Skin(0)
        PMCA.Adjust_Joints(0)
        PMCA.Copy_PMD(0,3)
