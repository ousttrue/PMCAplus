const std = @import("std");
const zcc = @import("compile_commands");

pub fn build(b: *std.Build) void {
    var targets = std.ArrayList(*std.Build.Step.Compile).init(b.allocator);

    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const dll = b.addSharedLibrary(.{
        .target = target,
        .optimize = optimize,
        .name = "PMCA",
        .link_libc = true,
    });
    const install = b.addInstallArtifact(dll, .{
        .dest_sub_path = "PMCA.pyd",
    });
    b.getInstallStep().dependOn(&install.step);
    targets.append(dll) catch @panic("OOM");

    dll.addCSourceFiles(.{
        .root = b.path("sources"),
        .files = &.{
            "PMCA_PyMod.c",
            "PMCA_SDLMod.c",
            "PMCA_view.c",
            "mlib_PMD_rw01.c",
            "mlib_PMD_edit01.c",
        },
        .flags = &.{
            // "-std=gnu23",
        },
    });
    dll.addIncludePath(.{ .cwd_relative = "C:/Python311/include" });
    dll.addLibraryPath(.{ .cwd_relative = "C:/Python311/libs" });
    dll.linkSystemLibrary("Python311");

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

    zcc.createStep(b, "cdb", targets.toOwnedSlice() catch @panic("OOM"));
}
