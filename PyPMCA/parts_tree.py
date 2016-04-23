# coding: utf-8
import sys
import io
from logging import getLogger
logger = getLogger(__name__)
from PyPMCA.parts import PARTS
from PyPMCA.pmd import Observable
from PyPMCA.parts_assembler import Assembler


class PartNode:
    '''
    モデルのパーツツリー
    '''
    def __init__(self, joint, depth, part=None):
        self.joint = joint
        if not joint:
            a=0
        self.depth = depth
        self.connect(part)

    def __str__(self):
        indent='  ' * self.depth
        if self.part:
            return '{0}#{1} => {2}'.format(indent, self.joint, self.part.name)
        else:
            return '{0}#{1}'.format(indent, self.joint)

    @staticmethod
    def create_root():
        root=PartNode(None, -1)
        root.children=[PartNode('root', 0)]
        return root

    def get_selected(self):
        return self.children[self.selected]

    def connect(self, part):
        '''
        部品を接続する。childrenを更新する
        '''
        self.part=part
        if not self.part: 
            self.children=[]
            self.selected=-1
            return

        children=self.children
        def get_or_create_node(joint):
            for c in children:
                if c.joint==joint:
                    return c
            return PartNode(joint, self.depth+1)
        self.children = [get_or_create_node(x) for x in part.child_joints]
  
    def traverse(self):
        for i, x in enumerate(self.children):
            yield x
            for y in x.traverse():
                yield y
        
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
                lines.extend(x.node_to_text())
                lines.append(indent+'[Parent]')
            else:
                lines.append(indent+'None')
        return lines

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
                self.children[index].text_to_node(iio, parts_list)
                index+=1
          
            elif line[0] == '[Parent]':
                return

            elif line[0] == 'MATERIAL':
                return

      
class PartsTree:
    def __init__(self):
        self.tree_entry_observable=Observable()
        self.parts_entry_observable=Observable()
        # 全パーツのリスト
        self.parts_list=[]
        # ツリー初期化
        self.tree_root=PartNode.create_root()
        self.tree_entry_selected=-1
        self.update(0)

    def update(self, sel=None):
        '''
        ツリーリスト更新
        '''
        if sel==None:
            sel=self.tree_entry_selected 
        self.tree_entry=[x for x in self.tree_root.traverse()]
        self.tree_entry_selected=-1
        self.tree_entry_observable.notify(self.tree_entry, sel)
        self.select_node(sel)

    def load_CNL_lines(self, iio: io.IOBase):
        '''
        CharacterNodeListの読み込み
        '''
        self.tree_root=PartNode.create_root()
        self.tree_root.text_to_node(iio, self.parts_list)
        self.update(0)

    def get_parts_entry(self):
        node=self.tree_entry[self.tree_entry_selected]
        return [x for x in self.parts_list if node.joint in x.joints]

    def __update_parts_entry(self):
        '''
        パーツリスト更新
        '''
        if len(self.tree_entry)==0: return
        node=self.tree_entry[self.tree_entry_selected]
        self.parts_entry_observable.notify(self.get_parts_entry(), node.selected)

    def load_partslist(self, assets_dir, lines):
        '''
        パーツリスト読み込み
        '''
        for parts in PARTS.parse_partslist(assets_dir, lines):
            self.parts_list.append(parts)
        self.select_node(0)

    def select_node(self, sel_t):
        '''
        ツリーノード選択
        '''
        logger.debug('select_node: %d -> %d', self.tree_entry_selected, sel_t)
        if(self.tree_entry_selected==sel_t):return
        self.tree_entry_selected=sel_t
        self.__update_parts_entry()

    def select_part(self, sel):
        '''
        パーツ選択
        '''
        left_selected=self.tree_entry[self.tree_entry_selected]
        parts_entry=self.get_parts_entry()
        if sel>=0 and sel<len(parts_entry):
            right_selected=parts_entry[sel]
            left_selected.connect(right_selected)
            self.update(self.tree_entry_selected)

    def build(self):
        '''
        モデル組立て
        '''
        logger.info('Parts.Build')
        assembler=Assembler()
        assembler.assemble(self.tree_root)
