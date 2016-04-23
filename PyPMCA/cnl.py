# coding: utf-8
import io
from PyPMCA.parts_node import PartNode


def node_to_text(self):
    '''
    CNLに出力
    '''
    lines=[]
    for x in self.children:
        indent='  ' * (x.depth)
        if x.part:
            lines.append(indent+'[Name] %s'%(x.part.name))
            lines.append(indent+'[Path] %s'%(x.part.path))
            lines.append(indent+'[Child]')
            lines.extend(node_to_text(x))
            lines.append(indent+'[Parent]')
        else:
            lines.append(indent+'None')
    return lines

def load(iio: io.IOBase, parts_list):
    root=PartNode.create_root()
    text_to_node(root, iio, parts_list)
    return root

def text_to_node(self, iio: io.IOBase, parts_list):
    '''
    CNLを読み込み
    '''

    def find_part(name, path):
        if name != None:
            for y in parts_list:
                if y.name == name:
                    return y
        elif path != None:
            for y in parts_list:
                if y.path == path:
                    return y

    index = 0
    while iio.readable():
        line=iio.readline().strip()

        line = line.split(' ')
        if line[0] == 'None':
            index+=1
                
        elif line[0] == '[Name]':
            name = line[1]
                
        elif line[0] == '[Path]':
            if len(line) == 1:
                path = ''
            else:
                path = line[1]
                    
        elif line[0] == '[Child]':
            self.children[index].connect(find_part(name, path))
            text_to_node(self.children[index], iio, parts_list)
            index+=1
          
        elif line[0] == '[Parent]':
            return

        elif line[0] == 'MATERIAL':
            return

###############################################################################
# Transform
###############################################################################
class BONE_TRANS_DATA:
	def __init__(self, name='', length=1.0, thick=1.0, pos=[0.0,0.0,0.0], rot=[0.0,0.0,0.0], props={}):
		self.name  = name
		self.length= length
		self.thick = thick
		self.pos   = pos
		self.rot   = rot
		self.props=props

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


def transform_list_to_text(self):
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
	
def transform_text_to_list(lines):
	self=MODEL_TRANS_DATA(scale=1.0, bones=[], props={})
	
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
	return self
