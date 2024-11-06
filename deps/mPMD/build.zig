const std = @import("std");

const FLAGS = [_][]const u8{
    "-std=c23",
    "-DPMCA_BUILD",
};

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const lib = b.addStaticLibrary(.{
        .target = target,
        .optimize = optimize,
        .name = "mPMD",
        .link_libc = true,
    });
    lib.addCSourceFiles(.{
        .files = &.{
            "mlib_PMD_rw01.c",
            "mlib_PMD_edit01.c",
            "dbg.c",
        },
        .flags = &FLAGS,
    });

    b.installArtifact(lib);
}
