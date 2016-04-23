# coding: utf-8
'''
info_data = PMCA.getInfo(0)
info = INFO(info_data)
line = info.comment.split('\n')
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
'''

import PMCA
from PyPMCA.pmd import *
from logging import getLogger
logger = getLogger(__name__)


fsenc = sys.getfilesystemencoding()

class Assembler:
    def __init__(self):
        self.authors=[]
        self.licenses=[]

    def assemble(self, root):
        '''
        モデル0を初期化
        '''
        PMCA.Create_PMD(0)
        for x in root.traverse():
            if x.part:
                PMCA.Create_PMD(4)
                PMCA.Load_PMD(4, str(x.part.path).encode(fsenc, 'replace'))

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
                                for y in self.authors:
                                    if x == y:
                                        break
                                else:
                                    self.authors.append(x)
                
                    elif tmp[0] == 'License' or tmp[0] == 'license' or tmp[0] == 'ライセンス':
                        if len(tmp) > 1:
                            flag_license=True
                            tmp[1] = tmp[1].replace('　', ' ')
                            for x in tmp[1].split(' '):
                                for y in self.licenses:
                                    if x == y:
                                        break
                                else:
                                    self.licenses.append(x)
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

                PMCA.Add_PMD(0, 4)
                PMCA.Marge_PMD(0)
        PMCA.Sort_PMD(0)
                            