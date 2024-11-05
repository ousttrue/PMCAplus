const std = @import("std");
const sokol = @import("sokol");
const sg = sokol.gfx;
const glfw = @import("glfw_glue.zig");
const c = @cImport({
    @cInclude("mlib_PMD_rw01.h");
});

const State = struct {
    running: bool = true,
};

var g_thread: std.Thread = undefined;
var g_state = State{};

fn view(state: *State) void {
    std.debug.print("view start\n", .{});

    // create window and GL context via GLFW
    glfw.init(.{
        .title = "triangle-glfw.c",
        .width = 640,
        .height = 480,
        .no_depth_buffer = true,
    });
    defer glfw.shutdown();

    // setup sokol_gfx
    sg.setup(.{
        .environment = glfw.environment(),
        .logger = .{ .func = sokol.log.func },
    });
    // cleanup
    defer sg.shutdown();

    // a vertex buffer
    const vertices = [_]f32{
        // positions            // colors
        0.0,  0.5,  0.5, 1.0, 0.0, 0.0, 1.0,
        0.5,  -0.5, 0.5, 0.0, 1.0, 0.0, 1.0,
        -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0,
    };
    const vbuf = sg.makeBuffer(.{ .data = sg.asRange(&vertices) });

    // a shader
    const shd = sg.makeShader(.{
        .vs = .{ .source = 
        \\#version 330
        \\layout(location=0) in vec4 position;
        \\layout(location=1) in vec4 color0;
        \\out vec4 color;
        \\void main() {
        \\  gl_Position = position;
        \\  color = color0;
        \\}
        },
        .fs = .{ .source = 
        \\#version 330
        \\in vec4 color;
        \\out vec4 frag_color;
        \\void main() {
        \\  frag_color = color;
        \\}
        },
    });

    // a pipeline state object (default render states are fine for triangle)
    var pipDesc = sg.PipelineDesc{
        .shader = shd,
    };
    pipDesc.layout.attrs[0].format = .FLOAT3;
    pipDesc.layout.attrs[1].format = .FLOAT4;
    const pip = sg.makePipeline(pipDesc);

    // resource bindings
    var bind = sg.Bindings{};
    bind.vertex_buffers[0] = vbuf;

    // draw loop
    while (state.running and glfw.isRunning()) {
        sg.beginPass(.{ .swapchain = glfw.swapchain() });
        sg.applyPipeline(pip);
        sg.applyBindings(bind);
        sg.draw(0, 3, 1);
        sg.endPass();
        sg.commit();
        glfw.flush();
    }

    std.debug.print("view end\n", .{});
}

export fn view_begin() void {
    g_thread = std.Thread.spawn(.{}, view, .{&g_state}) catch @panic("thread");
}

export fn view_end() void {
    std.debug.print("join...", .{});
    g_state.running = false;
    g_thread.join();
    std.debug.print("done\n", .{});
}

export fn view_model_copy(src: *c.MODEL) void {
    _ = src;
}
