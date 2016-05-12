﻿# coding: utf-8
from itertools import chain
import shutil
import sys
import os
import io
import ctypes
sys.path.append('%s/converter'%(os.getcwd()))
import pathlib
import converter

from PyPMCA.parts_tree import *
from PyPMCA.parts_assembler import Assembler
from PyPMCA.material import *
from PyPMCA.material_entry import *
from PyPMCA.transform import *
from PyPMCA.pmd import *
from PyPMCA import cnl

from logging import getLogger
logger = getLogger(__name__)


APP_NAME = 'PMCA+ v0.0.1'


def load_list(fp):
	
	bone=[[],[]]
	skin=[[],[]]
	group=[[],[]]
	
	line = fp.readline()[:-1]
	line = fp.readline()[:-1]
	while line:
		line = fp.readline()[:-1]
		if line=='skin':
			break
		tmp = line.split(' ')
		bone[0].append(tmp[0].encode('cp932','replace'))
		bone[1].append(tmp[1].encode('cp932','replace'))
	
	while line:
		line = fp.readline()[:-1]
		if line=='bone_disp':
			break
		tmp = line.split(' ')
		skin[0].append(tmp[0].encode('cp932','replace'))
		skin[1].append(tmp[1].encode('cp932','replace'))
	
	while line:
		line = fp.readline()[:-1]
		if line=='end':
			break
		tmp = line.split(' ')
		group[0].append(tmp[0].encode('cp932','replace'))
		group[1].append(tmp[1].encode('cp932','replace'))
	
	LIST={'b':bone, 's':skin, 'g':group}
	
	return LIST


class MODELINFO:
	def __init__(self, name='PMCAモデル', name_l='PMCAモデル', comment='', name_eng='PMCA model', name_l_eng='PMCA generated model', comment_eng=''):
		self.name = name
		self.name_l = name_l
		self.comment = comment
		self.name_eng = name_eng
		self.name_l_eng = name_l_eng
		self.comment_eng = comment_eng


class SETTINGS:
    def __init__(self):
        self.export2folder = False


class PyPMCA:
    def __init__(self):
        self.model_update_observable=Observable()
        self.model_bb_observable=Observable()

        self.parts_tree=PartsTree()
        self.materials=MaterialSelector()
        self.transform=BodyTransform()
        self.modelinfo = MODELINFO()
        self.settings = SETTINGS()
        self.target_dir = './model/'
        self.init()
        self.update_level=-1

        def on_update(level):
            def __internal(*args):
                self.update_level=level
            return __internal

        def on_teee_entry(entry, sel):
             on_update(0)()
             self.materials.force_update(entry)
        self.parts_tree.tree_entry_observable.add(on_teee_entry)
        self.materials.color_select_observable.add(on_update(1))
        self.transform.transform_observable.add(on_update(2))

    def force_update_entry(self):
        self.parts_tree.update()
        self.materials.force_update()
        #self.transform.update_list()

    def update(self):
        '''
        パーツリスト、マテリアルリスト、トランスフォームの変更を描画モデルに反映する
        '''
        if self.update_level<0:
            # モデルの更新なし
            return

        if self.update_level==0:
            logger.info('Parts.Build')
            assembler=Assembler()
            new_model=assembler.assemble(self.parts_tree.root)
            new_model.Sort_PMD(
                self.LIST['b'][0], self.LIST['b'][1], 
                self.LIST['s'][0], self.LIST['s'][1], 
                self.LIST['g'][0], self.LIST['g'][1])
            PMCA.g_model[0]=new_model
            PMCA.g_model[0].CopyTo(PMCA.g_model[1])
            self.materials.ApplyToPmd(PMCA.g_model[0])
            PMCA.g_model[0].CopyTo(PMCA.g_model[2])
        elif self.update_level==1:
            logger.debug('update_material_select')
            PMCA.g_model[1].CopyTo(PMCA.g_model[0])
            self.materials.ApplyToPmd(PMCA.g_model[0])  
            PMCA.g_model[0].CopyTo(PMCA.g_model[2])
        elif self.update_level==2:
            logger.debug('update_transform')
            PMCA.g_model[2].CopyTo(PMCA.g_model[0])
        else:
            raise Exception("unknown update_level: " + self.update_level)

        self.transform.update(PMCA.g_model[0])
        PMCA.g_model[0].CopyTo(PMCA.g_model[3])
        self.update_level=-1
        self.name_update(PMCA.g_model[0])
        self.model_update_observable.notify()
        wht = PMCA.g_model[0].getWHT()
        self.model_bb_observable.notify(wht)

    def init(self):
        '''
        初期化。アセットリストをロードする
        '''

        with open('./assets/list.txt', 'r', encoding = 'utf-8-sig') as fp:
            self.LIST = load_list(fp)
            logger.info('load list.txt')

        for x in os.listdir('./assets/'):
            path=pathlib.Path('./assets/', x)
            if path.is_dir():
                try:
                    self.load_asset(path)
                except:
                    logger.error('fail to load %s', path)
                
    def load_asset(self, assets_dir: pathlib.Path):
        logger.info('load_asset %s', assets_dir)
        for x in assets_dir.glob('*.txt'):
            if x.is_file():
                with x.open('r', encoding = 'utf-8-sig') as fp:
                    lines=fp.readlines()
                    if lines[0]=='PMCA Parts list v2.0\n' :
                        self.parts_tree.load_partslist(assets_dir, lines[1:])
                    elif lines[0]=='PMCA Materials list v2.0\n' :
                        self.materials.load_material_list(assets_dir, lines[1:])
                    elif lines[0]=='PMCA Transform list v2.0\n' :
                        self.transform.load_transformlist(lines[1:])
                    else:
                        logger.warn('unknown line: %s %s', x, lines[0])

    def name_update(self, model):
        #str1, str2=self.get_license()
        str1='author'
        str2='license'
        #self.modelinfo.name = self.info_tab.frame.name.get()
        #self.modelinfo.name_l = self.info_tab.frame.name_l.get()
        #self.modelinfo.comment = self.info_tab.frame.comment.get('1.0',END)
        model.Set_Name_Comment(self.modelinfo.name,
            '%s\nAuthor:%s\nLicense:%s\n%s'%(self.modelinfo.name_l,str1,str2,self.modelinfo.comment), 
            self.modelinfo.name_eng,
            '%s\nAuthor:%s\nLicense:%s\n%s'%(self.modelinfo.name_l_eng,str1,str2,self.modelinfo.comment_eng))

    def load_CNL_File(self, path):
        name, long_name, tree, replace_map, transform_data=cnl.load_CNL_File(
            path, self.parts_tree.parts_list, self.materials.mats_list)
        self.modelinfo.name=name
        self.modelinfo.name_l=long_name
        self.parts_tree.root=tree
        self.parts_tree.update()
        self.materials.update_replace_map(replace_map)
        self.transform.transform_data=transform_data

    def get_materials(self):
        info = INFO(PMCA.g_model[0].getInfo())       
        for i in range(info.data["mat_count"]):
            yield MATERIAL(**PMCA.g_model[0].getMat(i))
        
    def save_CNL_File(self, path):
        cnl.save_CNL_File(path, self.modelinfo, 
                          self.parts_tree.root, 
                          self.get_materials(), self.materials.replace_map,
                          self.transform.transform_data[0])

    def save_PMD(self, name, model):
        if self.settings.export2folder:
            dirc = name[0:-4]
            os.mkdir(dirc)
            tmp = name.rsplit('/', 1)
            name = "%s/%s/%s"%(tmp[0] ,dirc.rsplit('/', 1)[1] ,tmp[1])
            
        logger.info('Write_PMD %s', name)
        if model.Write_PMD(name.encode(fsenc,'replace')) == 0:    
            #テクスチャコピー
            dirc = os.path.dirname(name)
            info_data = model.getInfo()
            info = INFO(info_data)
            for i in range(info.data["mat_count"]):
                mat = MATERIAL(**model.getMat(i))
                if mat.tex != '':
                    try:
                        shutil.copy(mat.tex_path, dirc)
                    except IOError:
                        logger.warning('コピー失敗:%s', mat.tex_path)
                if mat.sph != '':
                    try:
                        shutil.copy(mat.sph_path, dirc)
                    except IOError:
                        logger.warning('コピー失敗:%s', mat.sph_path)
    
            toon = model.getToon()
            for i,x in enumerate(model.getToonPath()):
                toon[i] = toon[i].decode('cp932','replace')
                #logger.debug(toon[i], x)
                if toon[i] != '':
                    try:
                        shutil.copy('toon/' + toon[i], dirc)
                    except IOError:
                        try:
                            shutil.copy('parts/' + toon[i], dirc)
                        except IOError:
                            logger.warning('コピー失敗:%s', toon[i])
    
    def batch_assemble(self, names):
        '''
        まとめてcnlをpmdに変換する
        '''
        self.save_CNL_File('./last.cnl')
        if type(names) is str:
            names = names.split(' ')
        for name in names:
            self.load_CNL_File(name)
            #self.refresh()
            
            name_PMD = name
            if name_PMD[-4:] == '.cnl':
                name_PMD = name_PMD[:-4] + '.pmd'
            else:
                name_PMD += '.pmd'
            self.save_PMD(name_PMD, PMCA.g_model[0])
        self.load_CNL_File('./last.cnl')
        #self.refresh()
        self.target_dir = name.rsplit('/',1)[0]
       
    def savecheck_PMD(self):
        #self.refresh(level=3)
        model = Get_PMD(0)
        
        errors=[]
        
        if len(model.info.name) > 20:
            errors.append('モデル名の長さが20byteを超えています:' + str(len(model.info.name)) + 'byte')
        if len(model.info.comment) > 256:
            errors.append('モデルコメントの長さが256byteを超えています:' + str(len(model.info.comment)) + 'byte')
        if len(model.info.name_eng) > 20:
            errors.append('英語モデル名の長さが20byteを超えています:' + str(len(model.info.name)) + 'byte')
        if len(model.info.comment_eng) > 256:
            errors.append('英語モデルコメントの長さが256byteを超えています:' + str(len(model.info.comment)) + 'byte')
        for x in model.mat:
            if (len(x.tex)+len(x.sph)) > 20:
                errors.append('材質"' + x.name + '"のテクスチャ+スフィアマップの長さが20byteを超えています:' + str(len(x.tex)+len(x.sph)) + 'byte')
        
        for x in model.bone:
            if len(x.name) > 20:
                errors.append('ボーン"' + x.name + '"の名前の長さが20byteを超えています:' + str(len(x.name)) + 'byte')
            if len(x.name_eng) > 20:
                errors.append('ボーン"' + x.name + '"の英語名の長さが20byteを超えています:' + str(len(x.name_eng)) + 'byte')
            i = x.parent
            count = 0
            bone_count = len(model.bone)
            while count < bone_count:
                if i >= bone_count:
                    break
                i=model.bone[i].parent
                count += 1
            else:
                errors.append('循環依存：%s'%(x.name))
        
        for x in model.skin:
            if len(x.name) > 20:
                errors.append('表情"' + x.name + '"の名前の長さが20byteを超えています:' + str(len(x.name)) + 'byte')
            if len(x.name_eng) > 20:
                errors.append('表情"' + x.name + '"の英語名の長さが20byteを超えています:' + str(len(x.name_eng)) + 'byte')
        
        for x in model.bone_grp:
            if len(x.name) > 50:
                errors.append('ボーングループ"' + x.name + '"の名前の長さが50byteを超えています:' + str(len(x.name)) + 'byte')
            if len(x.name_eng) > 50:
                errors.append('ボーングループ"' + x.name + '"の英語名の長さが50byteを超えています:' + str(len(x.name_eng)) + 'byte')
        
        for x in model.rb:
            if len(x.name) > 20:
                errors.append('剛体"' + x.name + '"の名前の長さが20byteを超えています:' + str(len(x.name)) + 'byte')
        
        for x in model.joint:
            if len(x.name) > 20:
                errors.append('ジョイント"' + x.name + '"の名前の長さが20byteを超えています:' + str(len(x.name)) + 'byte')
        
        for i,x in enumerate(model.face):
            for y in x:
                if y >= len(model.vt):
                    errors.append('面%dの頂点インデックスが不正です:%s'%(i, str(x)))
        
        for i,x in enumerate(model.vt):
            for y in x.bone_num:
                if y >= len(model.bone):
                    errors.append('頂点%dのボーンインデックスが不正です:%s'%(i, str(x)))
        
        if len(errors) == 0:
            errors.append('PMDとして正常に保存できます')
        
        return errors
    
    def check_PMD(self):
        #self.refresh(level=3)
        info_data = PMCA.getInfo(0)
        info = INFO(info_data)
        string = 'name :' + info.name
        string += '\ncomment :\n' + info.comment
        string += '\n頂点数 :' + str(info_data['vt_count'])
        string += '\n面数　 :' + str(info_data['face_count'])
        string += '\n材質数 :' + str(info_data['mat_count'])
        string += '\nボーン数 :' + str(info_data['bone_count'])
        string += '\nIK数   :' + str(info_data['IK_count'])
        string += '\n表情数 :' + str(info_data['skin_count'])
        string += '\nボーングループ数 :' + str(info_data['bone_group_count'])
        string += '\nボーン表示数 :' + str(info_data['bone_disp_count'])
        
        string += '\n\n英語対応 :' + str(info_data['eng_support'])
        string += '\n剛体数 :' + str(info_data['rb_count'])
        string += '\nジョイント数 :' + str(info_data['joint_count'])
        return string
            
    def propcheck_PMD(self):
        #self.refresh(level=3)
        model = Get_PMD(0)
        string = 'name :' + model.info.name
        string += '\ncomment :\n' + model.info.comment
        string += '\n\nname_en :' + model.info.name_eng
        string += '\ncomment_en :\n' + model.info.comment_eng
        string += '\n\n頂点数 :' + str(model.info.data['vt_count']) + '\n'
        for i,x in enumerate(model.vt):
            string += str(i) + '\n'
            string += 'loc:' + str(x.loc) + '\n'
            string += 'nor:' + str(x.nor) + '\n'
            string += 'uv:' + str(x.uv) + '\n'
            string += 'bone:' + str(x.bone_num) + '\n'
            string += 'weight:' + str(x.weight) + '\n'
            string += 'edge:' + str(x.edge) + '\n\n'
            
        string += '\n面数　 :' + str(model.info.data['face_count']) + '\n'
        for i,x in enumerate(model.face):
            string += str(x) + '\n'
        string += '\n材質数 :' + str(model.info.data['mat_count']) + '\n'
        for i,x in enumerate(model.mat):
            string += str(i) + '\n'
            string += 'diff_col:' + str(x.diff_col) + '\n'
            string += 'mirr_col:' + str(x.mirr_col) + '\n'
            string += 'spec_col:' + str(x.spec_col) + '\n'
            string += 'spec:' + str(x.spec) + '\n'
            string += 'alpha:' + str(x.alpha) + '\n'
            string += 'toon:' + str(x.toon) + '\n'
            string += 'edge:' + str(x.edge) + '\n'
            string += 'tex:' + x.tex + '\n'
            string += 'sph:' + x.sph + '\n'
            string += 'face_count:' + str(x.face_count) + '\n\n'
        
        string += '\nボーン数 :' + str(model.info.data['bone_count']) + '\n'
        for i,x in enumerate(model.bone):
            string += str(i) + '\n'
            string += 'name:' + x.name + '\n'
            string += 'name_en:' + x.name_eng + '\n'
            string += 'parent:' + str(x.parent) + '\n'
            string += 'tail:' + str(x.tail) + '\n'
            string += 'type:' + str(x.type) + '\n'
            string += 'IK:' + str(x.IK) + '\n'
            string += 'loc:' + str(x.loc) + '\n\n'
        
        string += '\nIK数   :' + str(model.info.data['IK_count']) + '\n'
        for i,x in enumerate(model.IK_list):
            string += str(i) + '\n'
            string += 'index:' + str(x.index) + '\n'
            string += 'tail_index:' + str(x.tail_index) + '\n'
            string += 'chain_len:' + str(x.chain_len) + '\n'
            string += 'iterations:' + str(x.iterations) + '\n'
            string += 'weight:' + str(x.weight) + '\n'
            string += 'child:' + str(x.child) + '\n\n'
            
        string += '\n表情数 :' + str(model.info.data['skin_count']) + '\n'
        for i,x in enumerate(model.skin):
            string += str(i) + '\n'
            string += 'name:' + x.name + '\n'
            string += 'name_en:' + x.name_eng + '\n'
            string += 'count:' + str(x.count) + '\n'
            string += 'type:' + str(x.type) + '\n\n'
            #string += 'data:' + x.data + '\n'
        
        string += '\nボーングループ数 :' + str(model.info.data['bone_group_count']) + '\n'
        for i,x in enumerate(model.bone_grp):
            string += str(i) + '\n'
            string += 'name:' + x.name + '\n'
            string += 'name_en:' + x.name_eng + '\n\n'
        
        string += '\nボーン表示数 :' + str(model.info.data['bone_disp_count']) + '\n'
        for i,x in enumerate(model.bone_dsp):
            string += str(i) + '\n'
            string += 'index:' + str(x.index) + '\n'
            string += 'group:' + str(x.group) + '\n\n'
        
        for i,x in enumerate(model.toon.name):
            string += '%d %s\n'%(i,x)
        
        
        string += '\n\n英語対応 :' + str(model.info.data['eng_support'])
        string += '\n\n剛体数 :' + str(model.info.data['rb_count']) + '\n'
        for i,x in enumerate(model.rb):
            string += str(i) + '\n'
            string += 'name:' + x.name + '\n\n'
        
        string += '\nジョイント数 :' + str(model.info.data['joint_count']) + '\n'
        for i,x in enumerate(model.joint):
            string += str(i) + '\n'
            string += 'name:' + x.name + '\n\n'
        
        return string

    def get_model(self):
        '''
        OpenGLにデータを渡す
        '''
        info=PMCA.g_model[0].getInfo()

        # vertices
        vertices=[]
        uvs=[]
        for v in (PMCA.g_model[0].getVt(i) for i in range(info['vt_count'])):
            loc=v['loc']
            vertices.append(loc[0])
            vertices.append(loc[1])
            vertices.append(-loc[2])
            uvs+=v['uv']
        # indices
        indices=list(chain.from_iterable((PMCA.g_model[0].getFace(i) for i in range(info['face_count']))))
        # materials
        colors=[]
        paths=[]
        indexCounts=[]
        for m in (PMCA.g_model[0].getMat(i) for i in range(info['mat_count'])):
            colors.append((m['diff_col'][0] * 2 + m['mirr_col'][0]) / 2.5 + m['spec_col'][0] / 4)
            colors.append((m['diff_col'][1] * 2 + m['mirr_col'][1]) / 2.5 + m['spec_col'][1] / 4)
            colors.append((m['diff_col'][2] * 2 + m['mirr_col'][2]) / 2.5 + m['spec_col'][2] / 4)
            #colors.append(m['alpha'])
            colors.append(1.0)
            tex=m['tex'].decode('cp932')
            texture_path=self.materials.get_texture_path(tex)
            if texture_path:
                paths.append(texture_path)
            else:
                paths.append(os.path.join(os.path.dirname(info['path']), m['tex']).replace(b'\\', b'/'))
            indexCounts.append(m['face_count']*3)

        assert(sum(indexCounts)==len(indices))
        return vertices, uvs, indices, colors, paths, indexCounts

    def get_vertices(self):
        '''
        info=PMCA.g_model[0].getInfo()
        vertices=(PMCA.g_model[0].getVt(i) for i in range(info['vt_count']))
        vertices=[-n if i % 3 == 2 else n
                for v in vertices
                for i, n in enumerate(v['loc'])]
        return (ctypes.c_float*len(vertices))(*vertices)
        '''
        vertices=PMCA.g_model[0].getVertices()
        return (ctypes.c_float * len(vertices)).from_buffer(vertices)

    def get_uvs(self):
        info=PMCA.g_model[0].getInfo()
        vertices=(PMCA.g_model[0].getVt(i) for i in range(info['vt_count']))
        return [n
                for v in vertices
                for n in v['uv']]

    def get_indices(self):
        info=PMCA.g_model[0].getInfo()
        return list(chain.from_iterable((PMCA.g_model[0].getFace(i) for i in range(info['face_count']))))

    def get_material_diffuse_list(self):
        info=PMCA.g_model[0].getInfo()
        colors=[]
        for m in (PMCA.g_model[0].getMat(i) for i in range(info['mat_count'])):
            colors.append((m['diff_col'][0] * 2 + m['mirr_col'][0]) / 2.5 + m['spec_col'][0] / 4)
            colors.append((m['diff_col'][1] * 2 + m['mirr_col'][1]) / 2.5 + m['spec_col'][1] / 4)
            colors.append((m['diff_col'][2] * 2 + m['mirr_col'][2]) / 2.5 + m['spec_col'][2] / 4)
            #colors.append(m['alpha'])
            colors.append(1.0)
        return colors

    def get_material_path_list(self):
        info=PMCA.g_model[0].getInfo()
        paths=[]
        for m in (PMCA.g_model[0].getMat(i) for i in range(info['mat_count'])):
            tex=m['tex'].decode('cp932')
            texture_path=self.materials.get_texture_path(tex)
            if texture_path:
                paths.append(texture_path)
            else:
                paths.append(os.path.join(os.path.dirname(info['path']), m['tex']).replace(b'\\', b'/'))
        return paths

    def get_material_indexcount_list(self):
        info=PMCA.g_model[0].getInfo()
        indexCounts=[]
        for m in (PMCA.g_model[0].getMat(i) for i in range(info['mat_count'])):
            indexCounts.append(m['face_count']*3)
        return indexCounts
