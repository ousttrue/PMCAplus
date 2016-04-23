# coding: utf-8


class PARTS:    
    '''
    読み込みパーツデータ
    '''
    def __init__(self):
        self.name=''
        self.path=''
        self.comment=''

        # connect parent
        self.joints = []

        # connect children
        self.child_joints = []

        self.props={}
        self.tree_current=-1
        self.parts_current=-1

    def __str__(self):
        return self.name

    @staticmethod
    def parse_partslist(assetdir, lines):
        parts_dir = assetdir
        active = PARTS()
        for line in (l.strip().replace('\t',' ') for l in lines):
            if line=='':continue
            if line.startswith('#'):continue
            if line=='NEXT':
                yield active
                active = PARTS()
                continue

            splited = line.split(' ', 1)
            key=splited[0]
            value=splited[1] if len(splited)>1 else ''
            if key=='SETDIR':
                parts_dir = parts_dir.joinpath(value)
            elif key=='[name]':
                active.name = value
            elif key=='[path]':
                active.path = parts_dir.joinpath(value)
            elif key=='[comment]':
                active.comment = value
            elif key=='[type]':
                active.joints = active.joints +value.split(',')
            elif key=='[joint]':
                if value.strip() != '':
                    active.child_joints = active.child_joints+value.split(',')
            elif key[:1] == '[' and key[-1:] == ']':
                if key[1:-1] in active.props:
                    active.props[key[1:-1]].append(value)
                else:
                    active.props[key[1:-1]] = [value]
        yield active
