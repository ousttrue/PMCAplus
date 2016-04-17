import os
os.environ['VS90COMNTOOLS']=os.environ['VS140COMNTOOLS']

from distutils.core import setup, Extension

module1 = Extension(
    'PMCA'
    , sources = [
        'PMCA_PyMod.c', 
        'mlib_PMD_edit01.c',
        'mlib_PMD_rw01.c',
        ]
    , include_dirs = [
        ]
    , library_dirs = [
        ]
    , libraries = [
        'OPENGL32',
        'GLU32',
        ]
    )

setup(
    name = 'PMCA'
    , version = '1.0'
    , description = 'pmca'
    , ext_modules = [module1]
    )

