const std = @import("std");

pub fn build(b: *std.Build) !void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    var arena_state = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const PMCA_dep = b.dependency("PMCA", .{
        .target = target,
        .optimize = optimize,
    });

    const sokol_dep = PMCA_dep.builder.dependency("sokol", .{
        .target = target,
        .optimize = optimize,
        .with_sokol_imgui = true,
        .gl = true,
    });

    const cimgui_dep = PMCA_dep.builder.dependency("cimgui", .{
        .target = target,
        .optimize = optimize,
    });

    const rowmath_dep = b.dependency("rowmath", .{});
    const rowmath = rowmath_dep.module("rowmath");

    const font_dep = b.dependency("hackgen", .{});

    const mpmd_dep = b.dependency("mPMD", .{
        .target = target,
        .optimize = optimize,
    });

    {
        const exe = b.addExecutable(.{
            .target = target,
            .optimize = optimize,
            .name = "pmcaz",
            .root_source_file = b.path("main.zig"),
        });
        const install_exe = b.addInstallArtifact(exe, .{});
        b.getInstallStep().dependOn(&install_exe.step);
        exe.root_module.addImport("sokol", sokol_dep.module("sokol"));
        exe.root_module.addImport("cimgui", cimgui_dep.module("cimgui"));
        exe.root_module.addImport("rowmath", rowmath);
        // exe.root_module.addImport("stb", &stb_dep.artifact("stb").root_module);
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

        // exe.linkLibrary(PMCA_dep.artifact("PMCA"));
        exe.root_module.addImport("PMCA", &PMCA_dep.artifact("PMCA").root_module);

        const options = b.addOptions();
        var self_exe_dir = try std.fs.cwd().openDir(font_dep.path("").getPath(b), .{});
        defer self_exe_dir.close();

        const font = try self_exe_dir.readFileAlloc(
            arena,
            "HackGenConsoleNF-Regular.ttf",
            1024 * 1024 * 15,
        );
        // std.fs.read
        options.addOption([]const u8, "font", font);
        exe.root_module.addOptions("config", options);
    }

    {
        const exe = b.addTest(.{
            .name = "pmcaz_test",
            .target = target,
            .optimize = optimize,
            .root_source_file = b.path("src//pmca_assembler.zig"),
        });
        const run = b.addRunArtifact(exe);
        b.step("test", "test").dependOn(&run.step);
    }
}
