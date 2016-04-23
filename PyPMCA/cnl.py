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
