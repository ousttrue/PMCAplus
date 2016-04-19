# coding: utf-8
import random
import PMCA
from PyPMCA.pmd import TOON, INFO, MATERIAL, Observable
from PyPMCA.material_entry import MATS, MATS_ENTRY
from logging import getLogger
logger = getLogger(__name__)


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


class MAT_REP_DATA:
    '''
    材質置換データ
    '''
    def __init__(self, mat, sel: MATS_ENTRY=None):
        self.mat=mat
        self.sel=sel if sel else mat.entries[0]


class MaterialSelector:
    def __init__(self):             
        self.material_entry_observable=Observable()
        self.material_entry_observable.add(lambda entry, sel_t: self.__update_color_entry())
        self.color_entry_observable=Observable()
        self.color_select_observable=Observable()

        self.mats_list=[]    #list of class MATS
        self.mat_entry = []
        self.color_entry = []
        self.replace_map={}

        self.toon= TOON()
        self.app = LicenseInfo()

        self.cur_mat = -1
        self.cur_color= -1

    def force_update(self, entry=None):
        self.__update_material_entry()

    def apply_entry(self, x:MATERIAL, m:MATS_ENTRY):
        if m.tex: 
            x.tex = m.tex
            x.tex_path = m.get_tex_path()
            x.sph = ''
            x.sph_path = ''
        if m.diff_rgb: x.diff_col=m.diff_rgb
        if m.spec_rgb: x.spec_col=m.spec_rgb
        if m.mirr_rgb: x.mirr_col=m.mirr_rgb
        if m.toon:
            toon = TOON()
            toon.path = PMCA.getToonPath(0)
            toon.name = PMCA.getToon(0)
            tmp = m.toon.split(' ')
            tmp[0] = int(tmp[0])
            toon.path[tmp[0]] = ('toon/' + tmp[1]).encode('cp932','replace')
            toon.name[tmp[0]] = tmp[1].encode('cp932','replace')                                              
            PMCA.setToon(0, toon.name)
            PMCA.setToonPath(0, toon.path)
            x.toon = tmp[0]

    def ApplyToPmd(self, num):
        '''
        PMDに反映する
        '''
        info = INFO(PMCA.getInfo(num))       
        for i in range(info.data["mat_count"]):
            m=MATERIAL(**PMCA.getMat(num, i))
            if m.tex in self.replace_map:
                self.apply_entry(m, self.replace_map[m.tex].sel)
                PMCA.setMat(num, i,
                            m.diff_col, m.alpha, 
                            m.spec, m.spec_col, 
                            m.mirr_col, 
                            m.toon, m.edge, m.face_count, 
                            m.tex.encode('cp932','replace'), 
                            m.sph.encode('cp932','replace'), 
                            m.tex_path.encode('cp932','replace'), 
                            m.sph_path.encode('cp932','replace')
                            )

    def list_to_text(self):
        '''
        CNLに選択状態を出力する
        '''
        info = INFO(PMCA.getInfo(num))       
        for i in range(info.data["mat_count"]):
            m=MATERIAL(**PMCA.getMat(num, i))
            if m.tex in self.replace_map:
                x=self.replace_map[m.tex]       
                yield '[Name] %s' % (x.mat.name)
                yield '[Sel] %s' % (x.sel.name)
                yield 'NEXT'
    
    def load_material_list(self, assets_dir, lines):
        '''
        マテリアルリストを読み込む
        '''
        for new_material in MATS.parse(assets_dir, lines):
            if len(new_material.entries)==0:continue
            isMerged=False
            for material in self.mats_list:
                if material.name==new_material.name:
                    material.entries += new_material.entries
                    isMerged=True
            if not isMerged:
                self.mats_list.append(new_material)
                self.replace_map[new_material.name]=MAT_REP_DATA(new_material)

        self.__update_material_entry()

    def load_CNL_lines(self, lines):
        '''
        CNLを読み込む
        '''
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
                for y in self.mats_list:
                    if y.name == tmp[0]:
                        tmp[2] = y
                        break
                else:
                    tmp[2] = None
                    continue
                
                for y in tmp[2].entries:
                    if y.name == tmp[1]:
                        if tmp[0] in self.replace_map:
                            self.replace_map[tmp[0]] = MAT_REP_DATA(tmp[2], y)
                            break

        self.__update_material_entry()

    def __update_material_entry(self, sel_t=0):
        '''
        マテリアルリストを更新する(ツリーが変化した時など)
        '''
        info = INFO(PMCA.getInfo(0))       
        self.cur_mat=sel_t
        self.cur_color=0
        self.mat_entry=[]
        #for i in range(info.data["mat_count"]):
        #    m=MATERIAL(**PMCA.getMat(0, i))
        #    for x in self.mats_list:
        #        if x.name==m.tex:
        #            self.mat_entry.append(x.name)
        self.mat_entry=[x for x in self.replace_map.keys()]
        self.material_entry_observable.notify(self.mat_entry, self.cur_mat)

    def __update_color_entry(self, sel_t=0):
        '''
        マテリアルカラーリストを更新する(左リストの選択が変った時など)
        '''
        if len(self.mat_entry)==0: return

        self.cur_mat = sel_t
        self.cur_color=0
        key=self.mat_entry[self.cur_mat]
        self.color_entry = [x.name for x in self.replace_map[key].mat.entries]
        self.color_entry_observable.notify(self.color_entry, self.cur_color)

    def select_material(self, sel_t):
        '''
        マテリアルリストが選択された
        '''
        if self.cur_mat==sel_t:return

        self.__update_color_entry(sel_t)

    def select_color(self, sel_t):
        '''
        マテリアルカラーが選択された
        '''
        if self.cur_color==sel_t:return
        self.cur_color=sel_t

        key=self.mat_entry[self.cur_mat]
        rep=self.replace_map[key]
        rep.sel = rep.mat.entries[sel_t]
        self.color_select_observable.notify()

    def random(self):
        '''
        マテリアルカラーをランダムに選択する
        '''
        for v in self.replace_map.values():
            random.seed()
            val=random.randint(0, len(x[1].mat.entries)-1)
            v.sel = v.mat.entries[val]
        self.color_select_observable.notify()

    def replace(self):
        '''
        マテリアル置き換えを実行する        
        '''
        logger.info("Material.Replace")
        self.ApplyToPmd(0)
        PMCA.Copy_PMD(0, 2)
