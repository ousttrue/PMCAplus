import os
os.environ['VS90COMNTOOLS']=os.environ['VS140COMNTOOLS']

from distutils.core import setup, Extension

module1 = Extension(
    'PMCA'
    , sources = [
        'PMCA_PyMod.c', 
        'mPMD_edit.c',
        'mPMD_rw.c',
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
