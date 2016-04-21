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
        parents_stack = [self]
        child_nums = [0]

        for line  in lines:
            if len(parents_stack) == 0:
                break
            line = line.split(' ')
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
                    parents_stack.append(curnode)
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
                    parents_stack.pop()
                    child_nums.pop()
                    child_nums[-1]+=1
            
            elif line[0] == '[Parent]':
                curnode = parents_stack.pop()
                child_nums.pop()
                if len(child_nums) > 0:
                    child_nums[-1]+=1
            elif line[0] == 'MATERIAL':
                break
      

class TREE_LIST:
    def __init__(self, node=None, depth=0, text='', c_num=-1, list_num=0):
        self.node = node
        self.depth= depth
        self.text = text
        self.c_num = c_num

    def get_parts_entry(self, parts_list):
        joint = self.node.parts.joint[self.c_num]
        parts_entry = [x for x in parts_list if x.has_joint(joint)]
        #parts_entry.append('load')
        parts_entry.append(None)
        '''
        def get_name(x):
            if isinstance(x, PARTS):
                return x.name
            if x=="load":
                return "#外部モデル"
            else:
                return "#NONE"
        return [get_name(x) for x in parts_entry]
        '''
        return parts_entry


class PartsTree:
    def __init__(self):
        self.tree_entry_observable=Observable()
        self.parts_entry_observable=Observable()
        # 全パーツのリスト
        self.parts_list=[]
        # ツリー初期化
        self.tree_root=NODE(parts = PARTS.create_root(), depth = -1, child=[None])   
        self.tree_entry_selected=-1
        self.update(0)

    def update(self, sel=None):
        '''
        ツリーリスト更新
        '''
        if sel==None:
            sel=self.tree_entry_selected 
        self.tree_entry=[x for x in self.tree_root.create_list()][1:]
        self.tree_entry_selected=-1
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

    def load_CNL_lines(self, lines):
        '''
        CharacterNodeListの読み込み
        '''
        self.tree_root.text_to_node(self.parts_list, lines)
        self.update(0)

    def __update_parts_entry(self):
        '''
        パーツリスト更新
        '''
        if len(self.tree_entry)==0: return
        item=self.tree_entry[self.tree_entry_selected]
        self.parts_entry_observable.notify(item.get_parts_entry(self.parts_list), item.node.list_num)

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
        parts_entry=self.tree_entry[self.tree_entry_selected].get_parts_entry(self.parts_list)
        if sel>=len(parts_entry): return

        if parts_entry[sel]==None:    #Noneを選択した場合
            node = None
        
        elif parts_entry[sel]=='load':    #外部モデル読み込み
            path = filedialog.askopenfilename(filetypes = [('Plygon Model Deta(for MMD)','.pmd'),('all','.*')], defaultextension='.pmd')
            if(path != ''):
                name = path.split('/')[-1]
                parts = PyPMCA.PARTS(name = name, path = path, props = {})
                node = PyPMCA.NODE(parts = parts, depth = self.tree_list[self.tree_entry_selected].node.depth+1, child=[])
                for x in node.parts.joint:
                    node.child.append(None)
            else:
                node = None               
                
        else:          
            node = NODE(parts = parts_entry[sel], depth = self.tree_entry[self.tree_entry_selected].node.depth+1, child=[])
            p_node=self.tree_entry[self.tree_entry_selected].node.child[self.tree_entry[self.tree_entry_selected].c_num]
            
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
            
        self.tree_entry[self.tree_entry_selected].node.child[self.tree_entry[self.tree_entry_selected].c_num] = node

        self.update(self.tree_entry_selected)

    def build(self):
        '''
        モデル組立て
        '''
        logger.info('Parts.Build')
        self.tree_root.assemble(self)
