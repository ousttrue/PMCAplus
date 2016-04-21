# coding: utf-8
import PMCA
import sys
from PyPMCA.pmd import *
from PyPMCA.parts import PARTS
from logging import getLogger
logger = getLogger(__name__)


sysenc = sys.getfilesystemencoding()


class NODE:    
    '''
    モデルのパーツツリー
    '''
    def __init__(self, parts = '', depth = 0, child = [], list_num=-1):
        self.parts = parts
        self.depth = depth
        self.child = child
        self.list_num = list_num
    
    def assemble(self, app):
        app.script_fin = []
        #PMCA.Create_PMD(0)
        PMCA.Load_PMD(0, self.parts.path.encode(sysenc,'replace'))
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
                tmp[1] = tmp[1].replace('　', ' ')
                app.authors = tmp[1].split(' ')
                
            elif tmp[0] == 'License' or tmp[0] == 'license' or tmp[0] == 'ライセンス':
                tmp[1] = tmp[1].replace('　', ' ')
                app.licenses = tmp[1].split(' ')
        for x in self.child:
            if x != None:
                x.assemble_child(app)
                    
        PMCA.Sort_PMD(0)
        
        for x in app.script_fin:
            argv = x.split()
            fp = open(argv[0], 'r', encoding = 'utf-8-sig')
            script = fp.read()
            exec(script)
            fp.close
        
            
    def assemble_child(self, app):
        pmpy = app
        
        PMCA.Create_PMD(4)
        PMCA.Load_PMD(4, str(self.parts.path).encode(sysenc, 'replace'))
        
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
                argv = x.split()
                fp = open(argv[0], 'r', encoding = 'utf-8-sig')
                script = fp.read()
                exec(script)
                fp.close
        
        PMCA.Add_PMD(0, 4)
        PMCA.Marge_PMD(0)
        
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
                x.assemble_child(app)
    
    def create_list(self):
        List = [TREE_LIST(node=self, depth=self.depth, text='  '*(self.depth) + self.parts.name)]
        for i,x in enumerate(self.child):
            if x != None:
                List.append(TREE_LIST(node=self, depth=self.depth+1, text='  '*(self.depth+1) +self.child[i].parts.name, c_num=i))
                x.list_add(List)
            elif self.parts.joint[i] != '':
                List.append(TREE_LIST(node=self, depth=self.depth+1, text='  '*(self.depth+1) + '#'+self.parts.joint[i], c_num=i))
        return List
    
    def list_add(self, List):
        for i,x in enumerate(self.child):
            if x != None:
                List.append(TREE_LIST(node=self, depth=self.depth+1, text='  '*(self.depth+1) +self.child[i].parts.name, c_num=i))
                x.list_add(List)
            elif self.parts.joint[i] != '':
                List.append(TREE_LIST(node=self, depth=self.depth+1, text='  '*(self.depth+1) + '#'+self.parts.joint[i], c_num=i))
    
    def recalc_depth(self, depth):
        self.depth = depth
        depth = depth+1
        for x in self.child:
            if x != None:
                x.recalc_depth(depth)
        
    def node_to_text(self):
        '''
        CNLに出力
        '''
        lines=[]
        lines.append('[Name] %s'%(self.parts.name))
        lines.append('[Path] %s'%(self.parts.path))
        lines.append('[Child]')
        for x in self.child:
            if x != None:
                lines.extend(x.node_to_text())
            else:
                lines.append('None')
        lines.append('[Parent]')
        return lines
    
    def text_to_node(self, parts_list, lines):
        '''
        CNLを読み込み
        '''
        tmp = [None,None]
        curnode = self
        parents = [self]
        child_nums = [0]
        count=0
        while lines[count] != 'PARTS':
            count+=1
        count+=1
        
        while count < len(lines):
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
                if len(child_nums) > 0:
                    child_nums[-1]+=1
            elif line[0] == 'MATERIAL':
                break
            count +=1
        
        
        self.recalc_depth
        
        return lines




class TREE_LIST:
    def __init__(self, node=None, depth=0, text='', c_num=-1, list_num=0):
        self.node = node
        self.depth= depth
        self.text = text
        self.c_num = c_num


class PartsTree:
    def __init__(self):
        self.tree_entry_observable=Observable()
        self.parts_entry_observable=Observable()
        # 全パーツのリスト
        self.parts_list=[]
        # 現在選択中のノードに対応するリスト(jointが一致する)
        self.parts_entry = []
        # パーツツリー
        self.tree_list = []
        self.tree_entry = []
        self.tree_current=-1
        self.parts_current=-1
        self.__init_parts_tree()

    def update(self):
        self.__update_tree_entry()

    def __init_parts_tree(self):
        '''
        ツリー初期化
        '''
        node =NODE(parts = PARTS.create_root(), depth = -1, child=[None])   
        self.tree_list = node.create_list()
        self.__update_tree_entry()

    def load_CNL_lines(self, lines):
        '''
        CharacterNodeListの読み込み
        '''
        self.tree_list[0].node.text_to_node(self.parts_list, lines)
        self.__update_tree_entry()

    def __update_tree_entry(self, sel=-1, parts_sel=-1):
        '''
        ツリーリスト更新
        '''
        self.tree_entry=[x for x in self.tree_list[0].node.create_list()][1:]
        self.tree_current=-1
        self.parts_entry=[]
        self.parts_current=parts_sel
        def get_name(x):
            i=x.c_num
            joint=x.node.parts.joint[i]
            node=x.node.child[i]
            if node:
                return "%s#%s => %s" %('  '*x.depth, joint, node.parts.name)
            else:
                return "%s#%s" % ('  '*x.depth, joint) 
        self.tree_entry_observable.notify([get_name(x) for x in self.tree_entry], sel)
        self.select_node(sel)

    def __update_parts_entry(self):
        '''
        パーツリスト更新
        '''
        if len(self.tree_entry)==0: return

        joint = self.tree_entry[self.tree_current].node.parts.joint[self.tree_entry[self.tree_current].c_num]
        self.parts_entry = []
        for x in self.parts_list:
            for y in x.type:
                if y == joint:
                    self.parts_entry.append(x)
                    break
        self.parts_entry.append('load')
        self.parts_entry.append(None)
        def get_name(x):
            if isinstance(x, PARTS):
                return x.name
            if x=="load":
                return "#外部モデル"
            else:
                return "#NONE"
        self.parts_entry_observable.notify([get_name(x) for x in self.parts_entry], self.tree_entry[self.tree_current].node.list_num)

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
        logger.debug('select_node %d', sel_t)
        if(self.tree_current==sel_t):return
        self.tree_current=sel_t
        self.__update_parts_entry()

    def select_part(self, sel):
        '''
        パーツ選択
        '''
        if self.parts_current==sel: return
        if sel>=len(self.parts_entry): return
        self.parts_current=sel

        if self.parts_entry[sel]==None:    #Noneを選択した場合
            node = None
        
        elif self.parts_entry[sel]=='load':    #外部モデル読み込み
            path = filedialog.askopenfilename(filetypes = [('Plygon Model Deta(for MMD)','.pmd'),('all','.*')], defaultextension='.pmd')
            if(path != ''):
                name = path.split('/')[-1]
                parts = PyPMCA.PARTS(name = name, path = path, props = {})
                node = PyPMCA.NODE(parts = parts, depth = self.tree_list[self.tree_current].node.depth+1, child=[])
                for x in node.parts.joint:
                    node.child.append(None)
            else:
                node = None               
                
        else:          
            node = NODE(parts = self.parts_entry[sel], depth = self.tree_entry[self.tree_current].node.depth+1, child=[])
            p_node=self.tree_entry[self.tree_current].node.child[self.tree_entry[self.tree_current].c_num]
            
            child_appended = []
            if p_node != None:
                for x in node.parts.joint:
                    node.child.append(None)
                    for j,y in enumerate(p_node.parts.joint):
                        if x == y:
                            for z in child_appended:
                                if z == y:
                                    break
                            else:
                                node.child[-1] = p_node.child[j]
                                child_appended.append(y)
                                break
            else:
                for x in node.parts.joint:
                    node.child.append(None)
            
        self.tree_entry[self.tree_current].node.child[self.tree_entry[self.tree_current].c_num] = node
        #self.tree_list[sel_t].node.list_num = sel

        self.__update_tree_entry(self.tree_current, self.parts_current)

    def build(self):
        '''
        モデル組立て
        '''
        logger.info('Parts.Build')
        x = self.tree_list[0].node
        if x == None:
            return

        x.assemble(self)
