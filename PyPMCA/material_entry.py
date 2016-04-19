# coding: utf-8
from logging import getLogger
logger = getLogger(__name__)


class MATS_ENTRY:
    def __init__(self, name, parts_dir):
        self.name=name
        self.parts_dir=parts_dir
        self.tex=None
        self.toon=None
        self.diff_rgb=None
        self.spec_rgb=None
        self.mirr_rgb=None # ambien
        self.author=None

    def get_tex_path(self):
        return str(self.parts_dir.joinpath(self.tex))

    def get_sph_path(self):
        return str(self.parts_dir.joinpath(self.sph))


class MATS:    
    '''
    読み込み材質データ
    '''
    def __init__(self):
        self.name=''
        self.comment=''
        self.entries=[]

    @staticmethod
    def parse(assets_dir, lines):
        '''
        PMCA Materials list v2.0

        をパースする。
        '''
        parts_dir = assets_dir
       
        active=MATS()
        for line in (l.strip().replace('\t',' ') for l in lines):
            if line=='': continue
            if line=='PMCA Materials list v2.0': continue
            if line.startswith('#'): continue
            if line=='NEXT':
                if len(active.entries) > 0:
                    yield active
                active=MATS()
                continue

            splited = line.split(' ', 1)
            key=splited[0]
            value = splited[1] if len(splited)>1 else ''

            if key=='SETDIR':
                parts_dir = assets_dir.joinpath(value)
                continue
            assert key[:1] == '[' and key[-1:] == ']', 'invalid [format]: '+key 
            key=key[1:-1]
            if key=='ENTRY':
                active_entry=MATS_ENTRY(value, parts_dir)
                active.entries.append(active_entry)
            elif key=='name':
                active.name = value
            elif key=='comment':
                active.comment = value
            elif key=='tex':
                active_entry.tex = value
            elif key=='sph':
                assert False, 'sph'
                active_entry.sph = value
            elif key=='toon':
                active_entry.toon = value
            elif key=='diff_rgb':
                active_entry.diff_rgb = [float(x) for x in value.split()]
            elif key=='spec_rgb':
                active_entry.spec_rgb = [float(x) for x in value.split()]
            elif key=='mirr_rgb':
                active_entry.mirr_rgb = [float(x) for x in value.split()]
            elif key=='author':
                active_entry.author = value
            else:
                assert False, 'unknown key: '+key

        yield active
