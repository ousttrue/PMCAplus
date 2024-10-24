const std = @import("std");
const zcc = @import("compile_commands");

pub fn build(b: *std.Build) void {
    var targets = std.ArrayList(*std.Build.Step.Compile).init(b.allocator);
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const lib = b.addStaticLibrary(.{
        .target = target,
        .optimize = optimize,
        .name = "mPMD",
        .link_libc = true,
    });
    lib.addCSourceFiles(.{
        .root = b.path("mPMD"),
        .files = &.{
            "mlib_PMD_rw01.c",
            "mlib_PMD_edit01.c",
        },
        .flags = &.{
            "-std=c23",
        },
    });

    const dll = b.addSharedLibrary(.{
        .target = target,
        .optimize = optimize,
        .name = "PMCA",
        .link_libc = true,
    });
    const install_dll = b.addInstallArtifact(dll, .{
        .dest_sub_path = "PMCA.pyd",
    });
    b.getInstallStep().dependOn(&install_dll.step);
    targets.append(dll) catch @panic("OOM");

    dll.addCSourceFiles(.{
        .root = b.path("src"),
        .files = &.{
            "PMCA_PyMod.c",
            "PMCA_SDLMod.c",
            "PMCA_view.c",
        },
        .flags = &.{
            "-std=c23",
        },
    });
    dll.addIncludePath(.{ .cwd_relative = "C:/Python311/include" });
    dll.addLibraryPath(.{ .cwd_relative = "C:/Python311/libs" });
    dll.linkSystemLibrary("Python311");
    dll.addIncludePath(b.path("mPMD"));
    dll.linkLibrary(lib);

    const sdl_dep = b.dependency("sdl", .{
        .target = target,
        .optimize = optimize,
    });
    dll.linkLibrary(sdl_dep.artifact("SDL"));
    dll.addIncludePath(sdl_dep.path("include"));

    const stb_dep = b.dependency("stb", .{
        .target = target,
        .optimize = optimize,
    });
    dll.linkLibrary(stb_dep.artifact("stb"));
    dll.addIncludePath(stb_dep.path(""));

    dll.linkSystemLibrary("GDI32");
    dll.linkSystemLibrary("WINMM");
    dll.linkSystemLibrary("OPENGL32");
    dll.linkSystemLibrary("GLU32");

    const exe = b.addExecutable(.{
        .target = target,
        .optimize = optimize,
        .name = "pmcaz",
        .root_source_file = b.path("src/main.zig"),
    });
    const install_exe = b.addInstallArtifact(exe, .{});
    b.getInstallStep().dependOn(&install_exe.step);

    const run = b.addRunArtifact(exe);
    run.step.dependOn(&install_exe.step);

    b.step("run", "run pmcaz").dependOn(&run.step);

    const sokol_dep = b.dependency("sokol", .{
        .target = target,
        .optimize = optimize,
        .with_sokol_imgui = true,
    });
    exe.root_module.addImport("sokol", sokol_dep.module("sokol"));

    const cimgui_dep = b.dependency("cimgui", .{
        .target = target,
        .optimize = optimize,
    });
    // inject the cimgui header search path into the sokol C library compile step
    const cimgui_root = cimgui_dep.namedWriteFiles("cimgui").getDirectory();
    sokol_dep.artifact("sokol_clib").addIncludePath(cimgui_root);
    sokol_dep.artifact("sokol_clib").addCSourceFile(.{ .file = b.path("deps/cimgui//custom_button_behaviour.cpp") });
    exe.root_module.addImport("cimgui", cimgui_dep.module("cimgui"));

    const rowmath_dep = b.dependency("rowmath", .{});
    const rowmath = rowmath_dep.module("rowmath");
    exe.root_module.addImport("rowmath", rowmath);

    const stbi_dep = b.dependency("stb", .{
        .target = target,
        .optimize = optimize,
    });
    exe.root_module.addImport("stb", &stbi_dep.artifact("stb").root_module);

    zcc.createStep(b, "cdb", targets.toOwnedSlice() catch @panic("OOM"));
}
