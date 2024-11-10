const std = @import("std");
const zcc = @import("compile_commands");

const FLAGS = [_][]const u8{
    "-std=c23",
    "-DPMCA_BUILD",
};

pub fn build(b: *std.Build) !void {
    var targets = std.ArrayList(*std.Build.Step.Compile).init(b.allocator);
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    {
        const PMCA_dep = b.dependency("PMCA", .{
            .target = target,
            .optimize = optimize,
        });
        b.installArtifact(PMCA_dep.artifact("PMCA"));
    }

    {
        const pmcaz_dep = b.dependency("pmcaz", .{
            .target = target,
            .optimize = optimize,
        });
        const artifact = pmcaz_dep.artifact("pmcaz");
        const install = b.addInstallArtifact(artifact, .{});
        b.getInstallStep().dependOn(&install.step);

        const run = b.addRunArtifact(artifact);
        run.step.dependOn(&install.step);

        b.step("run", "run pmcaz").dependOn(&run.step);
    }

    {
        const glfw_dep = b.dependency("glfw", .{
            .target = target,
            .optimize = optimize,
        });

        const cimgui_dep = b.dependency("cimgui", .{
            .target = target,
            .optimize = optimize,
        });

        const exe = b.addExecutable(.{
            .name = "imgui_hello",
            .target = target,
            .optimize = optimize,
        });
        exe.addCSourceFiles(.{
            .files = &.{
                "src/imgui_hello.cpp",
            },
        });
        const install = b.addInstallArtifact(exe, .{});
        b.getInstallStep().dependOn(&install.step);
        const run = b.addRunArtifact(exe);
        run.step.dependOn(&install.step);
        b.step("imgui_hello", "build imgui_hello").dependOn(&run.step);
        targets.append(exe) catch @panic("OOM");
        exe.linkLibCpp();
        const imgui_dep = cimgui_dep.builder.dependency("imgui", .{});
        exe.addIncludePath(imgui_dep.path(""));
        exe.addIncludePath(imgui_dep.path("backends"));
        exe.addIncludePath(glfw_dep.builder.dependency("glfw", .{}).path("include"));
        exe.linkLibrary(glfw_dep.artifact("glfw"));
        exe.addCSourceFiles(.{
            .root = imgui_dep.path(""),
            .files = &.{
                "imgui.cpp",
                "imgui_draw.cpp",
                "imgui_widgets.cpp",
                "imgui_tables.cpp",
                "imgui_demo.cpp",
                "backends/imgui_impl_glfw.cpp",
                "backends/imgui_impl_opengl3.cpp",
            },
        });
    }

    zcc.createStep(b, "cdb", targets.toOwnedSlice() catch @panic("OOM"));
}
