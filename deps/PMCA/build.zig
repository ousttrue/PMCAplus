const std = @import("std");
const sokolShdc = @import("build_shdc.zig").sokolShdc;

const FLAGS = [_][]const u8{
    "-std=c23",
    "-DPMCA_BUILD",
};

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const mpmd_dep = b.dependency("mPMD", .{
        .target = target,
        .optimize = optimize,
    });

    const glfw_dep = b.dependency("glfw", .{
        .target = target,
        .optimize = optimize,
    });

    const sokol_dep = b.dependency("sokol", .{
        .target = target,
        .optimize = optimize,
        .with_sokol_imgui = true,
        .gl = true,
    });
    const cimgui_dep = b.dependency("cimgui", .{
        .target = target,
        .optimize = optimize,
    });
    // inject the cimgui header search path into the sokol C library compile step
    const cimgui_root = cimgui_dep.namedWriteFiles("cimgui").getDirectory();
    sokol_dep.artifact("sokol_clib").addIncludePath(cimgui_root);
    sokol_dep.artifact("sokol_clib").addCSourceFile(.{
        .file = cimgui_dep.path("custom_button_behaviour.cpp"),
    });

    const rowmath_dep = b.dependency("rowmath", .{});
    const rowmath = rowmath_dep.module("rowmath");

    const stb_dep = b.dependency("stb", .{
        .target = target,
        .optimize = optimize,
    });

    const dll = b.addSharedLibrary(.{
        .target = target,
        .optimize = optimize,
        .name = "PMCA",
        .link_libc = true,
        .root_source_file = b.path("PMCA.zig"),
    });
    const install_dll = b.addInstallArtifact(dll, .{
        // .dest_sub_path = "PMCA.pyd",
    });
    b.getInstallStep().dependOn(&install_dll.step);
    dll.addCSourceFiles(.{
        // .root = b.path("src"),
        .files = &.{
            "PMCA.c",
            // "dsp.c",
            // "quat.c",
        },
        .flags = &FLAGS,
    });
    dll.step.dependOn(sokolShdc(b, target, "PMCA_view.glsl"));
    // dll.linkLibCpp();
    dll.addIncludePath(.{ .cwd_relative = "C:/Python311/include" });
    dll.addLibraryPath(.{ .cwd_relative = "C:/Python311/libs" });
    dll.linkSystemLibrary("Python311");
    dll.addIncludePath(mpmd_dep.path(""));
    dll.linkLibrary(mpmd_dep.artifact("mPMD"));
    dll.addIncludePath(glfw_dep.builder.dependency("glfw", .{}).path("include"));
    dll.linkLibrary(glfw_dep.artifact("glfw"));
    dll.root_module.addImport("sokol", sokol_dep.module("sokol"));
    dll.root_module.addImport("rowmath", rowmath);
    dll.linkLibrary(stb_dep.artifact("stb"));
    dll.addIncludePath(stb_dep.path(""));
    dll.linkSystemLibrary("WINMM");
}
