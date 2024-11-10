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
