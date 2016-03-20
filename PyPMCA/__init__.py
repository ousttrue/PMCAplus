# coding: utf-8

from PyPMCA.parts import *
from PyPMCA.material import *
from PyPMCA.transform import *
from PyPMCA.pmd import *


def load_list(fp):
	
	bone=[[],[]]
	skin=[[],[]]
	group=[[],[]]
	
	line = fp.readline()[:-1]
	line = fp.readline()[:-1]
	while line:
		line = fp.readline()[:-1]
		if line=='skin':
			break
		tmp = line.split(' ')
		bone[0].append(tmp[0].encode('cp932','replace'))
		bone[1].append(tmp[1].encode('cp932','replace'))
		#print(tmp)
	
	while line:
		line = fp.readline()[:-1]
		if line=='bone_disp':
			break
		tmp = line.split(' ')
		skin[0].append(tmp[0].encode('cp932','replace'))
		skin[1].append(tmp[1].encode('cp932','replace'))
		#print(tmp)
	
	while line:
		line = fp.readline()[:-1]
		if line=='end':
			break
		tmp = line.split(' ')
		group[0].append(tmp[0].encode('cp932','replace'))
		group[1].append(tmp[1].encode('cp932','replace'))
		#print(tmp)
	
	LIST={'b':bone, 's':skin, 'g':group}
	
	return LIST


class MODELINFO:
	def __init__(self, name='PMCAモデル', name_l='PMCAモデル', comment='', name_eng='PMCA model', name_l_eng='PMCA generated model', comment_eng=''):
		self.name = name
		self.name_l = name_l
		self.comment = comment
		self.name_eng = name_eng
		self.name_l_eng = name_l_eng
		self.comment_eng = comment_eng
