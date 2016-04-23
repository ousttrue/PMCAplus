# coding: utf-8

class PartNode:
    '''
    部品木
    '''
    def __init__(self, joint, depth, part=None):
        self.joint = joint
        self.depth = depth
        self.connect(part)

    def __str__(self):
        '''
        文字列表現
        '''
        indent='  ' * self.depth
        if self.part:
            return '{0}#{1} => {2}'.format(indent, self.joint, self.part.name)
        else:
            return '{0}#{1}'.format(indent, self.joint)

    @staticmethod
    def create_root():
        '''
        Rootを新規に作成する
        '''
        root=PartNode(None, -1)
        root.children=[PartNode('root', 0)]
        return root

    def connect(self, part):
        '''
        部品を接続する。childrenを更新する
        '''
        self.part=part
        if not self.part: 
            self.children=[]
            return

        children=self.children
        def get_or_create_node(joint):
            for c in children:
                if c.joint==joint:
                    return c
            return PartNode(joint, self.depth+1)
        self.children = [get_or_create_node(x) for x in part.child_joints]
  
    def traverse(self):
        '''
        部品を木の順番に返す
        '''
        for i, x in enumerate(self.children):
            yield x
            for y in x.traverse():
                yield y
