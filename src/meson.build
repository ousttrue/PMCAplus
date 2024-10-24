cc = meson.get_compiler('c')

py_mod = import('python')
py = py_mod.find_installation()
py_dep = py.dependency()

gl_dep = dependency('gl', required: true)
# glu_dep = dependency('glu', required: true)
glu_dep = cc.find_library('glu32')

deps = [py_dep, sdl_dep, stb_dep, gl_dep, glu_dep]

# if get_option('buildtype') == 'debug'
#     python_debug_dep = cc.find_library(
#         'python312_d',
#         dirs: 'C:/Python312/libs',
#         required: true,
#     )
#     deps += python_debug_dep
# endif

py.extension_module(
    'PMCA',
    'PMCA_PyMod.c',
    'PMCA_SDLMod.c',
    'PMCA_view.c',
    'mlib_PMD_rw01.c',
    'mlib_PMD_edit01.c',
    install: true,
    install_dir: 'bin',
    dependencies: deps,
    c_args: [
        # '-DPy_BUILD_CORE',
        '-D_USE_MATH_DEFINES',
    ],
)
