project('SDL_image', 'c')

sdl_dep = subproject('SDL-1.2').get_variable('sdl_dep')

sdl_image_inc = include_directories('.')
sdl_image_lib = static_library(
    'sdl_image',
    [
        'IMG.c',
        'IMG_bmp.c',
        'IMG_gif.c',
        'IMG_jpg.c',
        'IMG_lbm.c',
        'IMG_pcx.c',
        'IMG_png.c',
        'IMG_pnm.c',
        'IMG_tga.c',
        'IMG_tif.c',
        'IMG_webp.c',
        'IMG_xcf.c',
        'IMG_xpm.c',
        'IMG_xv.c',
        'IMG_xxx.c',
    ],
    include_directories: sdl_image_inc,
    c_args: [
        '-D_CRT_SECURE_NO_DEPRECATE',
        '-D_WINDOWS',
        '-D_WIN32_WINNT=0x0400',
    ],
    dependencies: [sdl_dep],
)

sdl_image_dep = declare_dependency(
    link_with: sdl_image_lib,
    include_directories: sdl_image_inc,
)
