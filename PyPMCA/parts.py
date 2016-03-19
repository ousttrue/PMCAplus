﻿# coding: utf-8
import PMCA
import sys
from PyPMCA.pmd import INFO

sysenc = sys.getfilesystemencoding()


def load_partslist(fp, parts_list):
	directry = ''
	active = PARTS(props = {})
	line = fp.readline()
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
			parts_list.append(active)
			active = PARTS(props = {})
		
		elif len(line)<2:
			pass
		elif line[0]=='[name]':
			active.name = line[1]
		elif line[0]=='[path]':
			active.path = directry+line[1]
		elif line[0]=='[comment]':
			active.comment = line[1]
		elif line[0]=='[type]':
			active.type = active.type+line[1].split(',')
		elif line[0]=='[joint]':
			active.joint = active.joint+line[1].split(',')
		elif line[0][:1] == '[' and line[0][-1:] == ']':
			if line[0][1:-1] in active.props:
				active.props[line[0][1:-1]].append(line[1])
			else:
				active.props[line[0][1:-1]] = [line[1]]
		line = fp.readline()
	parts_list.append(active)
	for x in parts_list:
		print(x.name, x.path)
	return parts_list


###PMCA操作関連
def tree_click(event):
	pass

def space(i):
	string = ''
	for x in range(i):
		string = string+'  '
	return string

###データ関連
class NODE:	#モデルのパーツツリー
	def __init__(self, parts = '', depth = 0, child = [], list_num=-1):
		self.parts = parts
		self.depth = depth
		self.child = child
		self.list_num = list_num
	
	def assemble(self, num, app):
		app.script_fin = []
		PMCA.Create_PMD(num)
		PMCA.Load_PMD(num, self.parts.path.encode(sysenc,'replace'))
		info_data = PMCA.getInfo(0)
		info = INFO(info_data)
		line = info.comment.split('\n')
		
		app.authors=[]
		app.licenses=[]
		if info.name != '':
			app.authors=['Unknown']
			app.licenses=['Nonfree']
		
		pmpy = app
		pmpy.functions = PMCA
		if 'script_pre' in self.parts.props:
			for x in self.parts.props['script_pre']:
				argv = x.split()
				fp = open(argv[0], 'r', encoding = 'utf-8-sig')
				script = fp.read()
				exec(script)
				fp.close
		
		if 'script_post' in self.parts.props:
			for x in self.parts.props['script_post']:
				argv = x.split()
				fp = open(argv[0], 'r', encoding = 'utf-8-sig')
				script = fp.read()
				exec(script)
				fp.close
		
		if 'script_fin' in self.parts.props:
			app.script_fin.extend(self.parts.props['script_fin'])
		
		for x in line:
			tmp = x.split(':', 1)
			if len(tmp)==1:
				tmp = x.split('：', 1)
			if tmp[0] == 'Author' or tmp[0] == 'author' or tmp[0] == 'Creator' or tmp[0] == 'creator' or tmp[0] == 'モデル制作':
				print(tmp[1])
				tmp[1] = tmp[1].replace('　', ' ')
				app.authors = tmp[1].split(' ')
				
			elif tmp[0] == 'License' or tmp[0] == 'license' or tmp[0] == 'ライセンス':
				tmp[1] = tmp[1].replace('　', ' ')
				app.licenses = tmp[1].split(' ')
		print('パーツのパス:%s'%(self.parts.path))
		for x in self.child:
			if x != None:
				x.assemble_child(num, app)
					
		PMCA.Sort_PMD(num)
		
		for x in app.script_fin:
			argv = x.split()
			fp = open(argv[0], 'r', encoding = 'utf-8-sig')
			script = fp.read()
			exec(script)
			fp.close
		
			
	def assemble_child(self, num, app):
		pmpy = app
		print('パーツのパス:%s'%(self.parts.path))
		
		PMCA.Create_PMD(4)
		PMCA.Load_PMD(4, self.parts.path.encode(sysenc,'replace'))
		
		info_data = PMCA.getInfo(4)
		info = INFO(info_data)
		line = info.comment.split('\n')
		flag_author=False
		flag_license=False
		for x in line:
			tmp = x.split(':', 1)
			if len(tmp)==1:
				tmp = x.split('：', 1)
			if tmp[0] == 'Author' or tmp[0] == 'author' or tmp[0] == 'Creator' or tmp[0] == 'creator' or tmp[0] == 'モデル制作':
				if len(tmp) > 1:
					flag_author=True
					tmp[1] = tmp[1].replace('　', ' ')
					for x in tmp[1].split(' '):
						for y in app.authors:
							if x == y:
								break
						else:
							app.authors.append(x)
				
			elif tmp[0] == 'License' or tmp[0] == 'license' or tmp[0] == 'ライセンス':
				if len(tmp) > 1:
					flag_license=True
					tmp[1] = tmp[1].replace('　', ' ')
					for x in tmp[1].split(' '):
						for y in app.licenses:
							if x == y:
								break
						else:
							app.licenses.append(x)
		if info.name != '':
			if flag_author == False:
				for x in app.authors:
					if x == 'Unknown':
						break
				else:
					app.authors.append('Unknown')
			if flag_license == False:
				for x in app.licenses:
					if x == 'Nonfree':
						break
				else:
					app.licenses.append('Nonfree')
					
		
		if 'script_pre' in self.parts.props:
			for x in self.parts.props['script_pre']:
				print('プレスクリプト実行')
				argv = x.split()
				fp = open(argv[0], 'r', encoding = 'utf-8-sig')
				script = fp.read()
				exec(script)
				fp.close
		
		PMCA.Add_PMD(num, 4)
		PMCA.Marge_PMD(num)
		
		if 'script_post' in self.parts.props:
			for x in self.parts.props['script_post']:
				argv = x.split()
				fp = open(argv[0], 'r', encoding = 'utf-8-sig')
				script = fp.read()
				exec(script)
				fp.close
		if 'script_fin' in self.parts.props:
			app.script_fin.extend(self.parts.props['script_fin'])
		
		
		for x in self.child:
			if x != None:
				x.assemble_child(num,app)
	
	def create_list(self):
		List = [TREE_LIST(node=self, depth=self.depth, text=space(self.depth) + self.parts.name)]
		for i,x in enumerate(self.child):
			if x != None:
				List.append(TREE_LIST(node=self, depth=self.depth+1, text=space(self.depth+1) +self.child[i].parts.name, c_num=i))
				x.list_add(List)
			elif self.parts.joint[i] != '':
				List.append(TREE_LIST(node=self, depth=self.depth+1, text=space(self.depth+1) + '#'+self.parts.joint[i], c_num=i))
		return List
	
	def list_add(self, List):
		for i,x in enumerate(self.child):
			if x != None:
				List.append(TREE_LIST(node=self, depth=self.depth+1, text=space(self.depth+1) +self.child[i].parts.name, c_num=i))
				x.list_add(List)
			elif self.parts.joint[i] != '':
				List.append(TREE_LIST(node=self, depth=self.depth+1, text=space(self.depth+1) + '#'+self.parts.joint[i], c_num=i))
	
	def recalc_depth(self, depth):
		self.depth = depth
		depth = depth+1
		for x in self.child:
			if x != None:
				x.recalc_depth(depth)
		
	def node_to_text(self):
		lines=[]
		lines.append('[Name] %s'%(self.parts.name))
		lines.append('[Path] %s'%(self.parts.path))
		lines.append('[Child]')
		print(self.parts.path)
		for x in self.child:
			if x != None:
				lines.extend(x.node_to_text())
			else:
				lines.append('None')
		lines.append('[Parent]')
		return lines
	
	def text_to_node(self, parts_list, lines):
		tmp = [None,None]
		curnode = self
		parents = [self]
		child_nums = [0]
		count=0
		while lines[count] != 'PARTS':
			#print(lines[i])
			count+=1
		count+=1
		
		while count < len(lines):
			print('count = %d'%(count))
			line = lines[count].split(' ')
			if len(parents) == 0:
				break
			if line[0] == 'None':
				tmp = [None,None]
				child_nums[-1]+=1
				
			elif line[0] == '[Name]':
				tmp[0] = line[1]
				
			elif line[0] == '[Path]':
				if len(line) == 1:
					tmp[1] = ''
				else:
					tmp[1] = line[1]
					
			elif line[0] == '[Child]':
				
				tp = None
				print(tmp[0], len(parents))
				if tmp[0] != None:
					for y in parts_list:
						if y.name == tmp[0]:
							tp = y
							break
					else:
						for y in parts_list:
							if y.path == tmp[1]:
								tp = y
								break
				
				if tp != None:
					print(curnode.parts.name ,len(curnode.child), child_nums[-1])
					curnode.child[child_nums[-1]] = NODE(parts = y, depth = curnode.depth+1, child=[])
					parents.append(curnode)
					curnode = curnode.child[child_nums[-1]]
					child_nums.append(0)
					for x in curnode.parts.joint:
						curnode.child.append(None)
				
				else:
					depc = 1
					while depc == 0:
						count += 1
						if lines[count] == '[Child]':
							depc += 1
						if lines[count] == '[Parent]':
							depc -= 1
					parents.pop()
					child_nums.pop()
					child_nums[-1]+=1
			
			elif line[0] == '[Parent]':
				curnode = parents.pop()
				child_nums.pop()
				print("up", len(parents))
				if len(child_nums) > 0:
					child_nums[-1]+=1
			elif line[0] == 'MATERIAL':
				break
			count +=1
		
		
		self.recalc_depth
		
		return lines


class PARTS:	#読み込みパーツデータ
	def __init__(self, name='', comment='', path='', t=[], joint=[], props={}):
		self.name=name
		self.comment=comment
		self.path=path
		self.type=t
		self.joint=joint
		self.props=props


class TREE_LIST:
	def __init__(self, node=None, depth=0, text='', c_num=-1, list_num=0):
		self.node = node
		self.depth= depth
		self.text = text
		self.c_num = c_num
