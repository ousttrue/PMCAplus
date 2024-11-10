const std = @import("std");
const sokol = @import("sokol");
const sg = sokol.gfx;
const glfw = @import("glfw_glue.zig");
const c = @cImport({
    @cInclude("mlib_PMD_rw01.h");
});
const Renderer = @import("Renderer.zig");
const rowmath = @import("rowmath");
const OrbitCamera = rowmath.OrbitCamera;

const State = struct {
    mutex: std.Thread.Mutex = .{},
    running: bool = true,
    model: c.MODEL = undefined,
    copy: u32 = 0,
    orbit: OrbitCamera = .{
        .shift = .{ .x = 0, .y = 8, .z = 20 },
    },

    fn copy_model(self: *@This(), src: *c.MODEL) void {
        self.mutex.lock();
        defer self.mutex.unlock();
        _ = c.delete_PMD(&self.model);
        _ = c.copy_PMD(&self.model, src);
        self.copy += 1;
    }
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
    });
    defer glfw.shutdown();

    // setup sokol_gfx
    sg.setup(.{
        .environment = glfw.environment(),
        .logger = .{ .func = sokol.log.func },
    });
    // cleanup
    defer sg.shutdown();

    var renderer = Renderer.init();

    // draw loop
    while (state.running) {
        var input = glfw.isRunning() orelse {
            break;
        };
        state.orbit.frame(input.*);
        input.mouse_wheel = 0;
        const m = state.orbit.viewProjectionMatrix();

        if (state.copy > 0) {
            state.mutex.lock();
            defer state.mutex.unlock();
            defer state.copy = 0;
            renderer.loadModel(std.heap.c_allocator, &state.model) catch
                @panic("loadModel");
        }

        {
            renderer.begin(glfw.swapchain(), m);
            defer renderer.end();
            if (renderer.dsp) |dsp| {
                dsp.render();
            }
        }

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
    g_state.copy_model(src);
}
