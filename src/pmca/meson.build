cc = meson.get_compiler('c')

py_mod = import('python')
py = py_mod.find_installation()
py_dep = py.dependency()

gl_dep = dependency('gl', required: true)
# glu_dep = dependency('glu', required: true)
glu_dep = cc.find_library('glu32')

glfw_dep = dependency(
    'glfw3',
    default_options: ['default_library=static'],
)
imgui_dep = dependency(
    'imgui',
    default_options: ['default_library=static'],
)
glew_dep = dependency(
    'glew',
    default_options: ['default_library=static'],
)
deps = [py_dep, glfw_dep, imgui_dep, gl_dep, glu_dep, plog_dep, glew_dep]

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
    'PMCA_PyMod.cpp',
    'pmd_model.cpp',
    'quat.cpp',
    'ioutil.cpp',
    install: true,
    install_dir: 'bin',
    dependencies: deps,
    c_args: [
        # '-DPy_BUILD_CORE',
        '-D_USE_MATH_DEFINES',
    ],
)
