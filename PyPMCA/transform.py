# coding: utf-8
import PMCA
import PMCA_dialogs
from PyPMCA.pmd import INFO, BONE, Observable
from PyPMCA import cnl
from logging import getLogger
logger = getLogger(__name__)


def load_translist(lines, trans_list):
	trans_list.append(cnl.MODEL_TRANS_DATA(bones=[]))
	
	mode = 0
	
	for line in lines:
		line = line.rstrip('\n').replace('\t',' ').split(' ', 1)
		if line[0]=='':
			pass
		if line[0][:1]=='#':
			pass
		elif line[0]=='NEXT':
			trans_list.append(cnl.MODEL_TRANS_DATA(scale=0.0, bones=[]))
			mode = 0
		
		elif len(line)<2:
			pass
		
		elif line[0]=='[ENTRY]':
			trans_list[-1].bones.append(cnl.BONE_TRANS_DATA(name = line[1], length=0.0, thick=0.0, props = {}))
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

	'''
	mats_list.append(mats_list[-1])
	if mats_list[-1].entries[-1].__class__.__name__ == 'MATS_ENTRY':
		mats_list[-1].entries.append(mats_list[-1].entries[-1])
	'''
	
	return trans_list


	
				
		


class BodyTransform:
    def __init__(self):
        self.transform_observable=Observable()
        self.transform_select_observable=Observable()
        self.transform_sel=-1
        self.transform_data = []
        self.transform_list = []
        self.transform_data=[cnl.MODEL_TRANS_DATA(scale=1.0, bones=[], props={})]
        self.data=None

    def refresh(self):
        self.transform_observable.notify()

    def load_transformlist(self, lines):
        self.transform_list = load_translist(lines, self.transform_list)
        self.tmp = []
        for x in self.transform_list:
            self.tmp.append(x.name)

    def clear(self):
        self.transform_data = [cnl.MODEL_TRANS_DATA(scale=1.0, pos=[0.0, 0.0, 0.0], rot=[0.0, 0.0, 0.0], bones=[], props={})]
        self.transform_observable.notify()

    def select_transform(self, sel):
        if self.transform_sel==sel:return
        self.transform_sel=sel
        self.cancel()
        t = self.transform_list[sel]

        self.data = cnl.MODEL_TRANS_DATA(name = t.name,
                             scale=1.0, 
                             bones=[BONE_TRANS_DATA(name=x.name) for x in t.bones], 
                             pos=[0.0, 0.0, 0.0], 
                             rot=[0.0, 0.0, 0.0], 
                             props={})
        self.transform_data.append(self.data)

        self.transform_select_observable.notify(t)

    def cancel(self):
        if not self.data:return
        self.transform_data.remove(self.data)
        self.data=None
        self.transform_observable.notify()

    def apply(self):
        if not self.data:return
        self.transform_data[0].scale = self.data.scale * self.transform_data[0].scale
        for i,x in enumerate(self.transform_data[0].pos):
            x += self.data.pos[i]
        for i,x in enumerate(self.transform_data[0].rot):
            x += self.data.rot[i]
        for x in self.data.bones:
            tmp = None
            for y in self.transform_data[0].bones:
                if y.name==x.name:
                    tmp = y
                    break
            else:
                self.transform_data[0].bones.append(PyPMCA.BONE_TRANS_DATA(name=x.name))
                tmp = self.transform_data[0].bones[-1]
            
            tmp.length = tmp.length*x.length
            tmp.thick = tmp.thick * x.thick
            for i,y in enumerate(tmp.pos):
                y += x.pos[i]
            for i,y in enumerate(tmp.rot):
                y += x.rot[i]
        self.transform_data.remove(self.data)
        self.data=None
        self.transform_observable.notify()
           
    def setValue(self, var):
        if not self.data:return
        weight = self.transform_list[self.transform_sel].scale
        self.data.scale = weight * var+1-weight
        
        weight = self.transform_list[self.transform_sel].pos
        for i,x in enumerate(weight):
            self.data.pos[i] = x * var
        
        weight = self.transform_list[self.transform_sel].rot
        for i,x in enumerate(weight):
            self.data.rot[i] = x * var

       
        for i,x in enumerate(self.transform_list[self.transform_sel].bones):
            self.data.bones[i].length = x.length * var+1-x.length
            self.data.bones[i].thick = x.thick * var+1-x.thick
            for j,y in enumerate(x.pos):
                self.data.bones[i].pos[j] = y * var
            for j,y in enumerate(x.rot):
                self.data.bones[i].rot[j] = y * var
        self.transform_observable.notify()

    def update(self, model: PMCA.Model):
        info_data = model.getInfo()
        info = INFO(info_data)
            
        tmpbone = []
        for i in range(info_data["bone_count"]):
            tmp = model.getBone(i)
            tmpbone.append(BONE(tmp['name'], tmp['name_eng'], tmp['parent'], tmp['tail'], tmp['type'], tmp['IK'], tmp['loc']))
        refbone = None
        refbone_index = None
        for i,x in enumerate(tmpbone):
            if x.name == "右足首":
                refbone = x
                refbone_index = i
                break
            
        for y in self.transform_data:
            model.Resize_Model(y.scale)
            for x in y.bones:
                model.Resize_Bone(x.name.encode('cp932','replace'), x.length, x.thick)
                model.Move_Bone(x.name.encode('cp932','replace'),x.pos[0], x.pos[1], x.pos[2])
            
        if refbone!=None:
            newbone=None
            tmp = model.getBone(refbone_index)
            newbone = BONE(tmp['name'], tmp['name_eng'], tmp['parent'], tmp['tail'], tmp['type'], tmp['IK'], tmp['loc'])
                
            dy = refbone.loc[1] - newbone.loc[1]
            for x in tmpbone:
                i = x.parent
                count = 0
                while i < info_data["bone_count"] and count < info_data["bone_count"]:
                    if tmpbone[i].name == 'センター':
                        model.Move_Bone(x.name.encode('cp932','replace'), 0, dy, 0)
                        break
                    i=tmpbone[i].parent
                    count += 1
                
            model.Move_Bone('センター'.encode('cp932','replace'), 0, dy, 0)
            model.Move_Bone('+センター'.encode('cp932','replace'), 0, -dy, 0)
            
        for y in self.transform_data:
            model.Move_Model(y.pos[0],y.pos[1],y.pos[2])
            
        model.Update_Skin()
        model.Adjust_Joints()
