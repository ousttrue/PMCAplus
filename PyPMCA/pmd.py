#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os.path
import os
import tkinter
import tkinter.filedialog

import PMCA

#インポートパスにカレントディレクトリを加える
sys.path.append(os.getcwd())

from logging import getLogger
logger = getLogger(__name__)



###C-Pythonデータ変換関連
class INFO:
	def __init__(self, dic):
		self.name     = dic['name'].decode('cp932','replace')
		self.name_eng = dic['name_eng'].decode('cp932','replace')
		self.comment     = dic['comment'].decode('cp932','replace')
		self.comment_eng = dic['comment_eng'].decode('cp932','replace')
		self.eng_support = dic['eng_support']
		self.skin_index = dic['skin_index']
		self.data     = dic

class VT:
	def __init__(self, loc=[0, 0, 0], nor=[0, 0, 0], uv=[0, 0], bone_num1=0, bone_num2=0, weight=1, edge=0):
		self.loc  = loc
		self.nor  = nor
		self.uv   = uv
		self.bone_num = [bone_num1, bone_num2]
		self.weight = weight
		self.edge = edge

class MATERIAL:
	def __init__(self, diff_col, alpha, spec, spec_col, mirr_col, toon, edge, face_count, tex, sph, tex_path, sph_path):
		self.diff_col = diff_col
		self.alpha = alpha
		self.spec  = spec
		self.spec_col = spec_col
		self.mirr_col = mirr_col
		self.toon = toon
		self.edge = edge
		self.face_count = face_count
		self.tex = tex.decode('cp932','replace')
		self.sph = sph.decode('cp932','replace')
		self.tex_path = tex_path.decode('cp932','replace')
		self.sph_path = sph_path.decode('cp932','replace')
		

class BONE:
	def __init__(self, name, name_eng, parent, tail, btype, IK, loc):
		if type(name) == type(b''):
			name = name.decode('cp932','replace')
		if type(name_eng) == type(b''):
			name_eng = name_eng.decode('cp932','replace')
		self.name     = name
		self.name_eng = name_eng
		self.parent   = parent
		self.tail     = tail
		self.type     = btype
		self.IK       = IK
		self.loc      = loc
		

class IK_LIST:
	def __init__(self, index, t_index, length, ite, weight, c_index):
		self.index = index
		self.tail_index = t_index
		self.chain_len  = length
		self.iterations = ite
		self.weight     = weight
		self.child      = c_index

class SKIN_DATA:
	def __init__(self, index, loc):
		self.index = index
		self.loc = loc

class SKIN:
	def __init__(self, name, name_eng, count, t, data):
		self.name     = name.decode('cp932','replace')
		self.name_eng = name_eng.decode('cp932','replace')
		self.count    = count
		self.type     = t
		self.data     = data

class BONE_GROUP:
	def __init__(self, name='', name_eng=''):
		self.name     = name.decode('cp932','replace')
		self.name_eng = name_eng.decode('cp932','replace')

class BONE_DISP:
	def __init__(self, index, bone_group):
		self.index    = index
		self.group    = bone_group

class TOON:
	def __init__(self):
		self.name    = None
		self.path    = None

class RB:
	def __init__(self, name = '', bone=0, group=0, target=0, shape=0, size=[1.0, 1.0, 1.0], loc=[0.0, 0.0, 0.0], rot=[0.0, 0.0, 0.0], prop=[0.0, 0.0, 0.0, 0.0, 0.0], t=0):
		self.name  = name.decode('cp932','replace')
		self.bone  = bone
		self.group = group
		self.target= target
		self.shape = shape
		self.size  = size
		self.loc   = loc
		self.rot   = rot
		self.mass  = prop[0]
		self.damp  = prop[1]
		self.rdamp = prop[2]
		self.res   = prop[3]
		self.fric  = prop[4]
		self.type  = t

class JOINT:
	def __init__(self, name = '', rbody=[0,0], loc=[0.0, 0.0, 0.0], rot=[0.0, 0.0, 0.0], limit=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], spring=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]):
		self.name  = name.decode('cp932','replace')
		self.rb    = rbody
		self.loc   = loc
		self.rot   = rot
		self.limit = limit
		self.spring= spring



class PMD:
	def __init__(self, info, vt, face, mat, bone, IK, skin, bone_group, bone_dsp, toon, rb, joint):
		self.info    = info
		self.vt      = vt
		self.face    = face
		self.mat     = mat
		self.bone    = bone
		self.IK_list = IK
		self.skin    = skin
		self.bone_grp= bone_group
		self.bone_dsp= bone_dsp
		self.toon    = toon
		self.rb      = rb
		self.joint   = joint
	
	def Set(self, num):
		pass


def Get_PMD(num, only = None):
	info_data = PMCA.getInfo(num)
	info = INFO(info_data)
	
	vt = []
	for i in range(info_data["vt_count"]):
		tmp = PMCA.getVt(num, i)
		vt.append(VT(**tmp))
	
	face = []
	for i in range(info_data["face_count"]):
		face.append(PMCA.getFace(num, i))
	
	mat = []
	for i in range(info_data["mat_count"]):
		tmp = PMCA.getMat(num, i)
		mat.append(MATERIAL(**tmp))
	
	bone = []
	for i in range(info_data["bone_count"]):
		tmp = PMCA.getBone(num, i)
		bone.append(BONE(tmp['name'], tmp['name_eng'], tmp['parent'], tmp['tail'], tmp['type'], tmp['IK'], tmp['loc']))
	
	ik = []
	for i in range(info_data["IK_count"]):
		tmp = PMCA.getIK(num, i)
		ik.append(IK_LIST(tmp['index'], tmp['tail'], tmp['len'], tmp['ite'], tmp['weight'], tmp['child']))
	
	skin = []
	for i in range(info_data["skin_count"]):
		tmp = PMCA.getSkin(num, i)
		
		data = []
		for j in range(tmp['count']):
			data.append(PMCA.getSkindata(num, i, j))
		skin.append(SKIN(tmp['name'],tmp['name_eng'], tmp['count'], tmp['type'], data))
	
	bone_group = []
	for i in range(info_data['bone_group_count']):
		tmp = PMCA.getBone_group(num, i)
		bone_group.append(BONE_GROUP(**tmp))
	
	bone_disp = []
	for i in range(info_data['bone_disp_count']):
		tmp = PMCA.getBone_disp(num, i)
		bone_disp.append(BONE_DISP(**tmp))
	
	toon = TOON()
	toon.name = PMCA.getToon(num)
	for (i,x) in enumerate(toon.name):
		toon.name[i] = x.decode('cp932','replace')
	
	toon.path = PMCA.getToonPath(num)
	for (i,x) in enumerate(toon.path):
		toon.path[i] = x.decode('cp932','replace')
	
	rb = []
	for i in range(info_data['rb_count']):
		tmp = PMCA.getRb(num, i)
		rb.append(RB(**tmp))
	
	joint = []
	for i in range(info_data['joint_count']):
		tmp = PMCA.getJoint(num, i)
		joint.append(JOINT(**tmp))
	
	
	return PMD(info, vt, face, mat, bone, ik, skin, bone_group, bone_disp, toon, rb, joint)

def Set_PMD(num, model):
	PMCA.Create_FromInfo(num, bytes(model.info.name.encode('cp932','replace')), bytes(model.info.comment.encode('cp932','replace')), bytes(model.info.name_eng.encode('cp932','replace')), bytes(model.info.comment_eng.encode('cp932','replace')), len(model.vt), len(model.face), len(model.mat), len(model.bone), len(model.IK_list), len(model.skin), len(model.bone_grp), len(model.bone_dsp), model.info.eng_support, len(model.rb), len(model.joint), len(model.info.skin_index), model.info.skin_index)
	
	for (i,x) in enumerate(model.vt):
		PMCA.setVt(num, i, x.loc, x.nor, x.uv, x.bone_num[0], x.bone_num[1], x.weight, x.edge)
	
	for (i,x) in enumerate(model.face):
		PMCA.setFace(num, i, x)
	
	for (i,x) in enumerate(model.mat):
		PMCA.setMat(num, i, x.diff_col, x.alpha, x.spec, x.spec_col, x.mirr_col, x.toon, x.edge, x.face_count, bytes(x.tex.encode('cp932','replace')), bytes(x.sph.encode('cp932','replace')), bytes(x.tex_path.encode('cp932','replace')), bytes(x.sph_path.encode('cp932','replace')))
	
	for (i,x) in enumerate(model.bone):
		PMCA.setBone(num, i, bytes(x.name.encode('cp932','replace')), bytes(x.name_eng.encode('cp932','replace')), x.parent, x.tail, x.type, x.IK, x.loc)
	
	for (i,x) in enumerate(model.IK_list):
		PMCA.setIK(num, i, x.index, x.tail_index, len(x.child), x.iterations, x.weight, x.child)
	
	for (i,x) in enumerate(model.skin):
		PMCA.setSkin(num, i, bytes(x.name.encode('cp932','replace')), bytes(x.name_eng.encode('cp932','replace')), len(x.data), x.type)
		for(j,y) in enumerate(x.data):
			PMCA.setSkindata(num, i, j, y["index"], y["loc"])
	
	for (i,x) in enumerate(model.bone_grp):
		PMCA.setBone_group(num, i, bytes(x.name.encode('cp932','replace')), bytes(x.name_eng.encode('cp932','replace')))
	for (i,x) in enumerate(model.bone_dsp):
		PMCA.setBone_disp(num, i, x.index, x.group)
	
	tmp = []
	logger.info(model.toon.name)
	for (i,x) in enumerate(model.toon.name):
		tmp.append(bytes(x.encode('cp932','replace')))
	PMCA.setToon(num, tmp)
	for (i,x) in enumerate(model.toon.path):
		tmp.append(bytes(x.encode('cp932','replace')))
	PMCA.setToonPath(num, tmp)
	
	
	for (i,x) in enumerate(model.rb):
		PMCA.setRb(num, i, bytes(x.name.encode('cp932','replace')), x.bone, x.group, x.target, x.shape, x.size, x.loc, x.rot, x.mass, x.damp, x.rdamp, x.res, x.fric, x.type)
	
	for (i,x) in enumerate(model.joint):
		PMCA.setJoint(num, i, bytes(x.name.encode('cp932','replace')), x.rb, x.loc, x.rot, x.limit, x.spring)
	
def Set_Name_Comment(num=0,name='',comment='',name_eng='',comment_eng=''):
	PMCA.Set_Name_Comment(num, name.encode('cp932','replace'), comment.encode('cp932','replace'), name.encode('cp932','replace'), comment.encode('cp932','replace'))
	

class Observable:
    def __init__(self):
        self.observers = []

    def add(self, callback):
        self.observers.append(callback)
        return lambda : self.observers.remove(callback)

    def notify(self, *args):
        for callback in self.observers:
            callback(*args)
