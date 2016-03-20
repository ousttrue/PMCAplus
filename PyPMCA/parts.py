# coding: utf-8
import PMCA
import sys
from PyPMCA.pmd import *


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
class NODE:    #モデルのパーツツリー
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
                #print(tmp[1])
                tmp[1] = tmp[1].replace('　', ' ')
                app.authors = tmp[1].split(' ')
                
            elif tmp[0] == 'License' or tmp[0] == 'license' or tmp[0] == 'ライセンス':
                tmp[1] = tmp[1].replace('　', ' ')
                app.licenses = tmp[1].split(' ')
        #print('パーツのパス:%s'%(self.parts.path))
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
        #print('パーツのパス:%s'%(self.parts.path))
        
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
                #print('プレスクリプト実行')
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
        '''
        CNLに出力
        '''
        lines=[]
        lines.append('[Name] %s'%(self.parts.name))
        lines.append('[Path] %s'%(self.parts.path))
        lines.append('[Child]')
        #print(self.parts.path)
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
            #print(lines[i])
            count+=1
        count+=1
        
        while count < len(lines):
            #print('count = %d'%(count))
            line = lines[count].split(' ')
            #print(line)
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
                #print(tmp[0], len(parents))
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
                    #print(curnode.parts.name ,len(curnode.child), child_nums[-1])
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
                #print("up", len(parents))
                if len(child_nums) > 0:
                    child_nums[-1]+=1
            elif line[0] == 'MATERIAL':
                break
            count +=1
        
        
        self.recalc_depth
        
        return lines


class PARTS:    #読み込みパーツデータ
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


class PartsTree:
    def __init__(self):
        self.tree_entry_observable=Observable()
        self.parts_entry_observable=Observable()
        self.parts_list=[]
        self.parts_entry = []
        self.tree_list = []
        self.tree_entry = []
        self.tree_current=0
        self.__init_parts_tree()

    def is_empty(self):
        return self.tree_list[0].node.child[0] == None

    def update(self):
        self.__update_tree_entry()

    def __init_parts_tree(self):
        '''
        ツリー初期化
        '''
        node =NODE(parts = PARTS(name = 'ROOT',joint=['root']), depth = -1, child=[None])   
        self.tree_list = node.create_list()
        self.__update_tree_entry()

    def load_CNL_lines(self, lines):
        '''
        CharacterNodeListの読み込み
        '''
        self.tree_list[0].node.text_to_node(self.parts_list, lines)
        self.__update_tree_entry()

    def __update_tree_entry(self):
        '''
        ツリーリスト更新
        '''
        self.tree_entry=[x for x in self.tree_list[0].node.create_list()][1:]
        def get_name(x):
            i=x.c_num
            joint=x.node.parts.joint[i]
            node=x.node.child[i]
            if node:
                return "%s#%s => %s" %('  '*x.depth, joint, node.parts.name)
            else:
                return "%s#%s" % ('  '*x.depth, joint) 
        self.tree_entry_observable.notify([get_name(x) for x in self.tree_entry], 0)
        self.select_node(0)

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

    def load_partslist(self, fp):
        '''
        パーツリスト読み込み
        '''
        self.parts_list = load_partslist(fp, self.parts_list)
        self.select_node(0)

    def select_node(self, sel_t):
        '''
        ツリーノード選択
        '''
        self.tree_current=sel_t
        self.__update_parts_entry()

    def select_part(self, sel):
        '''
        パーツ選択
        '''
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
            
            #print('>>', node.parts.name, '\n')
        self.tree_entry[self.tree_current].node.child[self.tree_entry[self.tree_current].c_num] = node
        #self.tree_list[sel_t].node.list_num = sel

        self.__update_tree_entry()

    def build(self):
        '''
        モデル組立て
        '''
        print('Parts.Build')
        x = self.tree_list[0].node
        if x == None:
            return

        # 0を組み立てて
        x.assemble(0, self)
        # 0を1にコピーする
        PMCA.Copy_PMD(0,1)
