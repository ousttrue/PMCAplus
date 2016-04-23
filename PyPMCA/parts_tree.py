# coding: utf-8
import sys
import io
from logging import getLogger
logger = getLogger(__name__)
from PyPMCA.parts import PARTS
from PyPMCA.pmd import Observable
from PyPMCA.parts_node import PartNode


class PartsTree:
    def __init__(self):
        self.tree_entry_observable=Observable()
        self.parts_entry_observable=Observable()
        # 全パーツのリスト
        self.parts_list=[]
        # ツリー初期化
        self.root=PartNode.create_root()
        self.tree_entry_selected=-1
        self.update(0)

    def update(self, sel=None):
        '''
        JointTree更新
        '''
        if sel==None:
            sel=self.tree_entry_selected 
        self.tree_entry=[x for x in self.root.traverse()]
        self.tree_entry_selected=-1
        self.tree_entry_observable.notify(self.tree_entry, sel)
        self.select_node(sel)

    def __get_parts_entry_and_selected(self):
        node=self.tree_entry[self.tree_entry_selected]
        entry=[x for x in self.parts_list if node.joint in x.joints]

        for i, e in enumerate(entry):
            if node.part==e:
                return entry, i

        return entry, -1

    def __update_parts_entry(self):
        '''
        パーツリスト更新
        '''
        if self.tree_entry_selected<0 or self.tree_entry_selected>=len(self.tree_entry): return
        node=self.tree_entry[self.tree_entry_selected]
        self.parts_entry_observable.notify(*self.__get_parts_entry_and_selected())

    def load_partslist(self, assets_dir, lines):
        '''
        パーツリスト読み込み
        '''
        for parts in PARTS.parse_partslist(assets_dir, lines):
            self.parts_list.append(parts)
        self.select_node(0)

    def select_node(self, sel_t):
        '''
        Joint選択
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
        parts_entry, _=self.__get_parts_entry_and_selected()
        if sel>=0 and sel<len(parts_entry):
            left_selected.connect(parts_entry[sel])
            self.update(self.tree_entry_selected)
