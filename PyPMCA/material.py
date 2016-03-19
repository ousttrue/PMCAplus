﻿# coding: utf-8
import PMCA
from PyPMCA.pmd import TOON, INFO, MATERIAL


def load_matslist(fp, mats_list):
	directry = ''
	
	mats_list.append(MATS(entries=[], props={}))
	
	line = fp.readline()
	mode = 0
	active = mats_list[-1]
	while line:
		line = line.rstrip('\n').replace('\t',' ').split(' ', 1)
		#print(line)
		if line[0]=='':
			pass
		if line[0][:1]=='#':
			pass
		elif line[0]=='SETDIR':
			directry = line[1]
		
		elif line[0]=='NEXT':
			if len(active.entries) == 0:
				mats_list.pop()
			mats_list.append(MATS(entries=[], props={}))
			active = mats_list[-1]
			mode = 0
		
		elif len(line)<2:
			pass
		
		elif line[0]=='[ENTRY]':
			active.entries.append(MATS_ENTRY(name = line[1], props = {}))
			mode = 1
		elif line[0]=='[name]':
			if mode == 0:
				for x in mats_list:
					if x.name == line[1]:
						active = x
						mats_list.pop()
						break
				else:
					active.name = line[1]
		elif line[0]=='[comment]':
			if mode == 0:
				active.comment = line[1]
		elif line[0]=='[tex]':
			active.entries[-1].props['tex'] = line[1]
			active.entries[-1].props['tex_path'] = directry+line[1]
		elif line[0]=='[sph]':
			active.entries[-1].props['sph'] = line[1]
			active.entries[-1].props['sph_path'] = directry+line[1]
		elif line[0][:1] == '[' and line[0][-5:] == '_rgb]':
			active.entries[-1].props[line[0][1:-1]] = line[1].split()
		elif line[0][:1] == '[' and line[0][-1:] == ']':
			if line[0][1:-1] in active.entries[-1].props:
				active.entries[-1].props[line[0][1:-1]].append(line[1])
			else:
				active.entries[-1].props[line[0][1:-1]] = [line[1]]
		line = fp.readline()
	'''
	mats_list.append(mats_list[-1])
	if mats_list[-1].entries[-1].__class__.__name__ == 'MATS_ENTRY':
		mats_list[-1].entries.append(mats_list[-1].entries[-1])
	'''
	for x in mats_list:
		print(x.name, x.comment, len(x.entries), x.props)
		for y in x.entries:
			print(y.name, y.props)
	
	return mats_list


class MAT_REP:	#材質置換
	def __init__(self, app=None):
		self.mat = {}
		self.toon= TOON()
		self.app = app
	
	def Get(self, mats_list, model=None, info=None, num = 0):
		if model == None:
			if info == None:
				info_data = PMCA.getInfo(num)
				info = INFO(info_data)
			mat = []
			for i in range(info.data["mat_count"]):
				tmp = PMCA.getMat(num, i)
				mat.append(MATERIAL(**tmp))
		else:
			info = model.info
			mat = model.mat
		
		for x in self.mat.values():
			x.num = -1
		
		for i in range(info.data["mat_count"]):
			for x in mats_list:
				if mat[i].tex == x.name and x.name != '':
					if self.mat.get(mat[i].tex) == None:
						self.mat[mat[i].tex] = MAT_REP_DATA(mat=x, num=i)
					else:
						self.mat[mat[i].tex].num = i
					
					if self.mat[mat[i].tex].sel == None:
						self.mat[mat[i].tex].sel = self.mat[mat[i].tex].mat.entries[0]
						for y in self.mat[mat[i].tex].mat.entries:
							print(y.props)
		
	def Set(self, model=None, info=None, num = 0):
		if model == None:
			if info == None:
				info_data = PMCA.getInfo(num)
				info = INFO(info_data)
			mat = []
			for i in range(info.data["mat_count"]):
				tmp = PMCA.getMat(num, i)
				mat.append(MATERIAL(**tmp))
		else:
			info = model.info
			mat = model.mat
		
		for i,x in enumerate(mat):
			if self.mat.get(x.tex) != None:
				rep = self.mat[x.tex].sel
				for k,v in rep.props.items():
					if k == 'tex':
						print("replace texture", x.tex, "to" ,v, "num =", i)
						x.tex = v
					elif k == 'tex_path':
						x.tex_path  = v
					elif k == 'sph':
						x.sph = v
					elif k == 'sph_path':
						x.sph_path  = v
					elif k == 'diff_rgb':
						x.diff_col = v
						for j,y in enumerate(x.diff_col):
							x.diff_col[j] = float(y)
					elif k == 'alpha':
						x.alpha = float(v)
					elif k == 'spec_rgb':
						#print(x.spec_col)
						x.spec_col = v
						for j,y in enumerate(x.spec_col):
							x.spec_col[j] = float(y)
					elif k == 'mirr_rgb':
						x.mirr_col = v
						for j,y in enumerate(x.mirr_col):
							x.mirr_col[j] = float(y)
					
					elif k == 'toon':
						toon = TOON()
						toon.path = PMCA.getToonPath(num)
						toon.name = PMCA.getToon(num)
						#print("toon")
						#print(toon.name)
						#print(toon.path)
						tmp = v[-1].split(' ')
						tmp[0] = int(tmp[0])
						toon.path[tmp[0]] = ('toon/' + tmp[1]).encode('cp932','replace')
						toon.name[tmp[0]] = tmp[1].encode('cp932','replace')
						
						#print(toon.name)
						#print(toon.path)
						
						PMCA.setToon(num, toon.name)
						PMCA.setToonPath(num, toon.path)
						x.toon = tmp[0]
						#print(tmp)
					elif k == 'author':
						for y in v[-1].split(' '):
							for z in self.app.authors:
								if z == y:
									break
							else:
								self.app.authors.append(y)
					elif k == 'license':
						for y in v[-1].split(' '):
							for z in self.app.licenses:
								if z == y:
									break
							else:
								self.app.licenses.append(y)
					
				#print(x.diff_col)
				#print(x.spec_col)
				PMCA.setMat(num, i, x.diff_col, x.alpha, x.spec, x.spec_col, x.mirr_col, x.toon, x.edge, x.face_count, bytes(x.tex.encode('cp932','replace')), bytes(x.sph.encode('cp932','replace')), bytes(x.tex_path.encode('cp932','replace')), bytes(x.sph_path.encode('cp932','replace')))
	
	def list_to_text(self):
		lines=[]
		
		for x in self.mat.values():
			lines.append('[Name] %s'%(x.mat.name))
			lines.append('[Sel] %s'%(x.sel.name))
			lines.append('NEXT')
		
		return lines
	
	def text_to_list(self, lines, mat_list):
		self.mat = {}
		tmp = ['','',None]
		i=0
		while lines[i] != 'MATERIAL':
			#print(lines[i])
			i+=1
		i+=1
		print('材質読み込み')
		for x in lines[i:]:
			x = x.split(' ')
			print(x)
			if x[0] == '[Name]':
				tmp[0] = x[1]
			elif x[0] == '[Sel]':
				tmp[1] = x[1]
			elif x[0] == 'NEXT':
				print(tmp[0])
				for y in mat_list:
					if y.name == tmp[0]:
						tmp[2] = y
						break
				else:
					tmp[2] = None
					print('Not found')
					continue
				
				for y in tmp[2].entries:
					print(y.name)
					if y.name == tmp[1]:
						print(tmp[0])
						self.mat[tmp[0]] = MAT_REP_DATA(num = -1, mat=tmp[2], sel=y)
						break
		
				
				
		

class MAT_REP_DATA:	#材質置換データ
	def __init__(self, num=-1, mat=None, sel=None):
		self.num=num
		self.mat=mat
		self.sel=sel


class MATS:	#読み込み材質データ
	def __init__(self, name='', comment='', entries=[], props={}):
		self.name=name
		self.comment=comment
		self.entries=entries
		self.props=props

class MATS_ENTRY:
	def __init__(self, name='', props={}):
		self.name=name
		self.props=props
