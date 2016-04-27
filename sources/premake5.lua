-- premake5.lua
location "build"

--PYTHON_DIR="C:/Python32"
PYTHON_DIR="C:/Anaconda3"

solution "PMCA"
do
    configurations { "Debug", "Release" }
    platforms { "Win64" }
end

filter "configurations:Debug"
do
    defines { "DEBUG", "_DEBUG" }
    flags { "Symbols" }
end

filter "configurations:Release"
do
    defines { "NDEBUG" }
    optimize "On"
end

filter { "platforms:Win32" }
do
    architecture "x32"
end
filter {"platforms:Win32", "configurations:Debug" }
    targetdir "build/Win32/Debug"
filter {"platforms:Win32", "configurations:Release" }
    targetdir "build/Win32/Release"

filter { "platforms:Win64" }
do
   architecture "x64"
end
filter {"platforms:Win64", "configurations:Debug" }
    targetdir "build/Win64/Debug"
filter {"platforms:Win64", "configurations:Release" }
    targetdir "build/Win64/Release"

project "PMCA"
do
    --kind "ConsoleApp"
    --kind "WindowedApp"
    --kind "StaticLib"
    kind "SharedLib"
    --language "C"
    language "C++"

    flags{ 
        --"WinMain" 
    }
    files { 
        "mPMD.h",
        "mPMD.cpp",
        "mPMD_edit.cpp",
        "mPMD_edit.h",
        "mPMD_rw.cpp",
        "mPMD_rw.h",
        "PMCA.cpp",
        "fixed_string.h",
    }
    includedirs {
        PYTHON_DIR.."/include",
    }
    defines {
        "WIN32",
        "_WINDOWS",
        "HAVE_ROUND",
    }
    buildoptions { 
        "/wd4996" 
    }
    libdirs {
        PYTHON_DIR.."/libs",
    }
    links {
    }
    postbuildcommands {
        'echo $(OutDir)$(TargetName).dll',
        'copy $(OutDir)$(TargetName).dll ..\\..\\$(TargetName).pyd',
        'copy $(OutDir)$(TargetName).pdb ..\\..\\$(TargetName).pdb',
    }
end

