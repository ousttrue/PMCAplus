# coding: utf-8
import random
import PMCA
from PyPMCA.pmd import TOON, INFO, MATERIAL, Observable
from logging import getLogger
logger = getLogger(__name__)


def parse_material_list(assets_dir, lines):
    parats_dir = assets_dir
       
    active=MATS(entries=[], props={})
    for line in (l.strip().replace('\t',' ') for l in lines):
        if line=='': continue
        if line.startswith('#'): continue
        if line=='NEXT':
            if len(active.entries) > 0:
                yield active
            active=MATS(entries=[], props={})

        splited = line.split(' ', 1)
        key=splited[0]
        value = splited[1] if len(splited)>1 else ''

        if key=='SETDIR':
            parats_dir = assets_dir.joinpath(value)       
        elif key=='[ENTRY]':
            active.entries.append(MATS_ENTRY(name = value, props = {}))
        elif key=='[name]':
            active.name = value
        elif key=='[comment]':
            active.comment = value
        elif key=='[tex]':
            active.entries[-1].props['tex'] = value
            active.entries[-1].props['tex_path'] = parats_dir.joinpath(value)
        elif key=='[sph]':
            active.entries[-1].props['sph'] = value
            active.entries[-1].props['sph_path'] = parats_dir.joinpath(value)
        elif key[:1] == '[' and key[-5:] == '_rgb]':
            active.entries[-1].props[key[1:-1]] = value.split()
        elif key[:1] == '[' and key[-1:] == ']':
            if key[1:-1] in active.entries[-1].props:
                active.entries[-1].props[key[1:-1]].append(value)
            else:
                active.entries[-1].props[key[1:-1]] = [value]
    yield active


class MAT_REP:    #材質置換
    def __init__(self, app=None):
        self.mat = {}
        self.toon= TOON()
        self.app = app
    
    def UpdateMaterial(self, mats_list, model=None, info=None, num = 0):
        '''
        mats_listで置き換え
        '''
        if model == None:
            if info == None:
                info_data = PMCA.getInfo(num)
                info = INFO(info_data)
            mat = []
            for i in range(info.data["mat_count"]):
                tmp = PMCA.getMat(num, i)
                mat.append(MATERIAL(**tmp))
        else:
            info = model.info
            mat = model.mat
        
        for x in self.mat.values():
            x.num = -1
        
        #logger.debug([m.tex for m in mat])
        #logger.debug([x.name for x in mats_list])
        for i, m in enumerate(mat):
            for x in mats_list:
                if m.tex == x.name and x.name != '':
                    if self.mat.get(m.tex) == None:
                        self.mat[m.tex] = MAT_REP_DATA(mat=x, num=i)
                    else:
                        self.mat[m.tex].num = i
                    
                    if self.mat[m.tex].sel == None:
                        self.mat[m.tex].sel = self.mat[m.tex].mat.entries[0]
        
    def ApplyToPmd(self, num):
        '''
        PMDに反映する
        '''
        info = INFO(PMCA.getInfo(num))
        mat = [MATERIAL(**PMCA.getMat(num, i)) for i in range(info.data["mat_count"])]
        
        for i,x in enumerate(mat):
            if self.mat.get(x.tex) != None:
                rep = self.mat[x.tex].sel
                for k,v in rep.props.items():
                    if k == 'tex':
                        x.tex = v
                    elif k == 'tex_path':
                        x.tex_path  = v
                    elif k == 'sph':
                        x.sph = v
                    elif k == 'sph_path':
                        x.sph_path  = v
                    elif k == 'diff_rgb':
                        x.diff_col = v
                        for j,y in enumerate(x.diff_col):
                            x.diff_col[j] = float(y)
                    elif k == 'alpha':
                        x.alpha = float(v)
                    elif k == 'spec_rgb':
                        x.spec_col = v
                        for j,y in enumerate(x.spec_col):
                            x.spec_col[j] = float(y)
                    elif k == 'mirr_rgb':
                        x.mirr_col = v
                        for j,y in enumerate(x.mirr_col):
                            x.mirr_col[j] = float(y)
                    
                    elif k == 'toon':
                        toon = TOON()
                        toon.path = PMCA.getToonPath(num)
                        toon.name = PMCA.getToon(num)
                        tmp = v[-1].split(' ')
                        tmp[0] = int(tmp[0])
                        toon.path[tmp[0]] = ('toon/' + tmp[1]).encode('cp932','replace')
                        toon.name[tmp[0]] = tmp[1].encode('cp932','replace')
                                               
                        PMCA.setToon(num, toon.name)
                        PMCA.setToonPath(num, toon.path)
                        x.toon = tmp[0]

                    elif k == 'author':
                        for y in v[-1].split(' '):
                            for z in self.app.authors:
                                if z == y:
                                    break
                            else:
                                self.app.authors.append(y)
                    elif k == 'license':
                        for y in v[-1].split(' '):
                            for z in self.app.licenses:
                                if z == y:
                                    break
                            else:
                                self.app.licenses.append(y)
                    
                PMCA.setMat(num, i,
                            x.diff_col, x.alpha, 
                            x.spec, x.spec_col, 
                            x.mirr_col, 
                            x.toon, x.edge, x.face_count, 
                            x.tex.encode('cp932','replace'), 
                            x.sph.encode('cp932','replace'), 
                            str(x.tex_path).encode('cp932','replace'), 
                            str(x.sph_path).encode('cp932','replace')
                            )
    
    def list_to_text(self):
        lines=[]
        
        for x in self.mat.values():
            lines.append('[Name] %s'%(x.mat.name))
            lines.append('[Sel] %s'%(x.sel.name))
            lines.append('NEXT')
        
        return lines
    
    def text_to_list(self, lines, mat_list):
        self.mat = {}
        tmp = ['','',None]
        i=0
        while lines[i] != 'MATERIAL':
            i+=1
        i+=1

        for x in lines[i:]:
            x = x.split(' ')
            if x[0] == '[Name]':
                tmp[0] = x[1]
            elif x[0] == '[Sel]':
                tmp[1] = x[1]
            elif x[0] == 'NEXT':
                for y in mat_list:
                    if y.name == tmp[0]:
                        tmp[2] = y
                        break
                else:
                    tmp[2] = None
                    continue
                
                for y in tmp[2].entries:
                    if y.name == tmp[1]:
                        self.mat[tmp[0]] = MAT_REP_DATA(num = -1, mat=tmp[2], sel=y)
                        break
        
                
                
        

class MAT_REP_DATA:    #材質置換データ
    def __init__(self, num=-1, mat=None, sel=None):
        self.num=num
        self.mat=mat
        self.sel=sel


class MATS:    
    '''
    読み込み材質データ
    '''
    def __init__(self, name='', comment='', entries=[], props={}):
        self.name=name
        self.comment=comment
        self.entries=entries
        self.props=props

class MATS_ENTRY:
    def __init__(self, name='', props={}):
        self.name=name
        self.props=props


class LicenseInfo:
    def __init__(self):
        self.licenses = []
        self.authors = []

    def get_entry(self):
        str1=''
        str2=''
        for x in self.authors:
            str1 += '%s '%(x)
        for x in self.licenses:
            str2 += '%s '%(x)
        logger.info('authors and license: %s/%s' , str1, str2)
        return str1, str2


class MaterialSelector:
    def __init__(self):             
        self.material_entry_observable=Observable()
        self.material_entry_observable.add(lambda entry, sel_t: self.__update_color_entry())
        self.color_entry_observable=Observable()
        #self.color_entry_observable.add(lambda entry, sel_t: self.replace())
        self.color_select_observable=Observable()

        self.mats_list=[]    #list of class MATS
        self.mat_entry = []
        self.color_entry = []
        self.license=LicenseInfo()       
        self.mat_rep = MAT_REP(app=self.license)
        self.cur_mat = -1
        self.cur_color= -1

    def is_empty(self):
        return len(self.mat_rep.mat)==0

    def force_update(self):
        self.__update_material_entry()

    def load_material_list(self, assets_dir, lines):
        '''
        マテリアルリストを読み込む
        '''
        for new_material in parse_material_list(assets_dir, lines):
            isMerged=False
            for material in self.mats_list:
                if material.name==new_material.name:
                    material.entries += new_material.entries
                    isMerged=True
            if not isMerged:
                self.mats_list.append(new_material)

        self.__update_material_entry()

    def load_CNL_lines(self, lines):
        '''
        CNLを読み込む
        '''
        self.mat_rep.text_to_list(lines, self.mats_list)
        self.__update_material_entry()

    def __update_material_entry(self, sel_t=0):
        '''
        マテリアルリストを更新する(ツリーが変化した時など)
        '''
        if self.is_empty(): return

        #self.__replace()
        #self.mat_rep.UpdateMaterial(self.mats_list, num=0)
        self.cur_mat=sel_t
        self.cur_color=0
        self.mat_entry = [[],[]]
        for v in self.mat_rep.mat.values():
            if v.num >= 0:
                self.mat_entry[0].append(v.mat.name + '  ' + v.sel.name)
                self.mat_entry[1].append(v.mat.name)
        self.material_entry_observable.notify(self.mat_entry[1], self.cur_mat)

    def __update_color_entry(self, sel_t=0):
        '''
        マテリアルカラーリストを更新する(左リストの選択が変った時など)
        '''
        if self.is_empty(): return
        if len(self.mat_entry[0])==0: return

        self.cur_mat = sel_t
        self.cur_color=0
        self.color_entry = []
        for x in self.mat_rep.mat[self.mat_entry[1][sel_t]].mat.entries:
            self.color_entry.append(x.name)
        self.color_entry_observable.notify(self.color_entry, self.cur_color)

    def select_material(self, sel_t):
        '''
        マテリアルリストが選択された
        '''
        if self.cur_mat==sel_t:return

        self.__update_color_entry(sel_t)
        return self.mat_rep.mat[self.mat_entry[1][sel_t]].mat.comment

    def select_color(self, sel_t):
        '''
        マテリアルカラーが選択された
        '''
        if self.cur_color==sel_t:return
        self.cur_color=sel_t

        self.mat_rep.mat[self.mat_entry[1][self.cur_mat]].sel = self.mat_rep.mat[self.mat_entry[1][self.cur_mat]].mat.entries[sel_t]
        self.color_select_observable.notify()

    def random(self):
        '''
        マテリアルカラーをランダムに選択する
        '''
        for x in self.mat_rep.mat.items():
            random.seed()
            x[1].sel = x[1].mat.entries[random.randint(0, len(x[1].mat.entries)-1)]
        self.color_select_observable.notify()

    def replace(self):
        '''
        マテリアル置き換えを実行する        
        '''
        logger.info("Material.Replace")
        self.mat_rep.UpdateMaterial(self.mats_list, num=0)
        self.mat_rep.ApplyToPmd(num=0)
        PMCA.Copy_PMD(0, 2)
