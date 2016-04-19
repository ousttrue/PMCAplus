# coding: utf-8
from logging import getLogger
logger = getLogger(__name__)


class MATS_ENTRY:
    def __init__(self, name='', props={}):
        self.name=name
        self.props=props

class MATS:    
    '''
    読み込み材質データ
    '''
    def __init__(self, name='', comment='', entries=[], props={}):
        self.name=name
        self.comment=comment
        self.entries=entries
        self.props=props

    @staticmethod
    def parse(assets_dir, lines):
        '''
        PMCA Materials list v2.0

        をパースする。
        '''
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
