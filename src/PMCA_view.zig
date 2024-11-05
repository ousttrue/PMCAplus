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

const Vertex = struct {
    loc: [3]f32,
    // nom: [3]f32,
    uv: [2]f32,
};

const Submesh = struct {
    draw_count: u32 = 0,
};

const DspModel = struct {
    bind: sg.Bindings = .{},
    materials: [128]Submesh = undefined,
    material_count: u32 = 0,
    index_count: u32 = 0,

    fn deinit(self: *@This()) void {
        sg.destroyBuffer(self.bind.vertex_buffers[0]);
        sg.destroyBuffer(self.bind.index_buffer);
    }

    fn render(self: @This()) void {
        sg.applyBindings(self.bind);
        // var offset: u32 = 0;
        // for (self.materials) |material| {
        //     sg.draw(offset, material.draw_count, 1);
        //     offset += material.draw_count;
        // }
        sg.draw(0, self.index_count, 1);
    }
};

const State = struct {
    mutex: std.Thread.Mutex = .{},
    running: bool = true,
    model: c.MODEL = undefined,
    copy: u32 = 0,
    dsp: ?DspModel = null,
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

    fn update_dsp(self: *@This(), allocator: std.mem.Allocator) !void {
        if (self.copy == 0) {
            return;
        }

        if (self.dsp) |*dsp| {
            dsp.deinit();
        }

        // create vertex buffer
        {
            self.mutex.lock();
            defer self.mutex.unlock();
            defer self.copy = 0;

            var dsp = DspModel{};

            var vertices = try allocator.alloc(Vertex, self.model.vt_count);
            defer allocator.free(vertices);
            for (0..self.model.vt_count) |i| {
                const src = self.model.vt[i];
                vertices[i] = .{
                    .loc = .{
                        src.loc[0],
                        src.loc[1],
                        -src.loc[2],
                    },
                    // .nom = self.model.vt[i].nor,
                    .uv = src.uv,
                };
            }
            const vbuf = sg.makeBuffer(.{ .data = sg.asRange(vertices) });
            dsp.bind.vertex_buffers[0] = vbuf;

            const ibuf = sg.makeBuffer(.{
                .type = .INDEXBUFFER,
                .data = .{
                    .ptr = self.model.vt_index,
                    .size = 2 * self.model.vt_index_count,
                },
            });
            dsp.bind.index_buffer = ibuf;
            dsp.index_count = self.model.vt_index_count;

            for (0..self.model.mat_count) |i| {
                dsp.materials[i].draw_count = self.model.mat[i].vt_index_count;
            }
            dsp.material_count = self.model.mat_count;

            self.dsp = dsp;
        }
    }

    fn render_dsp(self: @This()) void {
        if (self.dsp) |dsp| {
            dsp.render();
        }
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

    const renderer = Renderer.init();

    // draw loop
    while (state.running) {
        var input = glfw.isRunning() orelse {
            break;
        };
        state.orbit.frame(input.*);
        input.mouse_wheel = 0;
        const m = state.orbit.viewProjectionMatrix();

        state.update_dsp(std.heap.c_allocator) catch @panic("update_dsp");

        {
            renderer.begin(glfw.swapchain(), m);
            defer renderer.end();
            state.render_dsp();
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
