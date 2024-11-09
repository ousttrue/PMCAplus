const std = @import("std");
const zcc = @import("compile_commands");
const sokolShdc = @import("build_shdc.zig").sokolShdc;

const FLAGS = [_][]const u8{
    "-std=c23",
    "-DPMCA_BUILD",
};

pub fn build(b: *std.Build) void {
    var targets = std.ArrayList(*std.Build.Step.Compile).init(b.allocator);
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // dependencies
    const mpmd_dep = b.dependency("mPMD", .{
        .target = target,
        .optimize = optimize,
    });

    const rowmath_dep = b.dependency("rowmath", .{});
    const rowmath = rowmath_dep.module("rowmath");

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
    sokol_dep.artifact("sokol_clib").addCSourceFile(.{ .file = b.path("deps/cimgui//custom_button_behaviour.cpp") });

    const stb_dep = b.dependency("stb", .{
        .target = target,
        .optimize = optimize,
    });

    const dll = blk: {
        const dll = b.addSharedLibrary(.{
            .target = target,
            .optimize = optimize,
            .name = "PMCA",
            .link_libc = true,
            .root_source_file = b.path("src/PMCA_view.zig"),
        });
        const install_dll = b.addInstallArtifact(dll, .{
            // .dest_sub_path = "PMCA.pyd",
        });
        b.getInstallStep().dependOn(&install_dll.step);
        targets.append(dll) catch @panic("OOM");
        dll.addCSourceFiles(.{
            .root = b.path("src"),
            .files = &.{
                "PMCA.c",
                // "dsp.c",
                // "quat.c",
            },
            .flags = &FLAGS,
        });
        dll.step.dependOn(sokolShdc(b, target, "src/PMCA_view.glsl"));
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
        dll.linkSystemLibrary("GDI32");
        dll.linkSystemLibrary("WINMM");
        dll.linkSystemLibrary("OPENGL32");
        dll.linkSystemLibrary("GLU32");
        break :blk dll;
    };

    {
        const converter = b.addExecutable(.{
            .target = target,
            .optimize = optimize,
            .name = "converter",
            .link_libc = true,
        });
        converter.addCSourceFiles(.{
            .root = b.path("converter"),
            .files = &.{
                "PMCA_main.c",
                "PMCA_loadconf.c",
            },
            .flags = &FLAGS,
        });
        b.installArtifact(converter);
        converter.addIncludePath(mpmd_dep.path(""));
    }

    {
        const exe = b.addExecutable(.{
            .target = target,
            .optimize = optimize,
            .name = "pmcaz",
            .root_source_file = b.path("src/main.zig"),
        });
        const install_exe = b.addInstallArtifact(exe, .{});
        b.getInstallStep().dependOn(&install_exe.step);
        exe.root_module.addImport("sokol", sokol_dep.module("sokol"));
        exe.root_module.addImport("cimgui", cimgui_dep.module("cimgui"));
        exe.root_module.addImport("rowmath", rowmath);
        exe.root_module.addImport("stb", &stb_dep.artifact("stb").root_module);
        exe.addIncludePath(mpmd_dep.path(""));

        const run = b.addRunArtifact(exe);
        run.step.dependOn(&install_exe.step);
        b.step("run", "run pmcaz").dependOn(&run.step);

        {
            const install_docs = b.addInstallDirectory(.{
                .source_dir = cimgui_dep.artifact("cimgui_clib").getEmittedDocs(),
                .install_dir = .prefix,
                .install_subdir = "docs",
            });

            const docs_step = b.step("docs", "Copy documentation artifacts to prefix path");
            docs_step.dependOn(&install_docs.step);
        }

        exe.linkLibrary(dll);
    }

    zcc.createStep(b, "cdb", targets.toOwnedSlice() catch @panic("OOM"));
}
