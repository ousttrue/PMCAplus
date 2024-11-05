const std = @import("std");
const sokol = @import("sokol");
const sg = sokol.gfx;
const rowmath = @import("rowmath");
const InputState = rowmath.InputState;
const OrbitCamera = rowmath.OrbitCamera;
const pmca_parts = @import("pmca_parts.zig");
const pmca_material = @import("pmca_material.zig");
const pmca_transform = @import("pmca_transform.zig");
const pmca_assembler = @import("pmca_assembler.zig");
const Renderer = @import("Renderer.zig");

const state = struct {
    var allocator: std.mem.Allocator = undefined;
    var parts_list: []const pmca_parts.Parts = undefined;
    var material_list: []const pmca_material.Material = undefined;
    var transform_list: []const pmca_transform.Transform = undefined;
    var assembler: pmca_assembler.Assembler = undefined;
    var renderer: Renderer = undefined;
    var input = InputState{};
    var orbit: OrbitCamera = .{
        .shift = .{ .x = 0, .y = 8, .z = 20 },
    };
};

var fetch_buffer: [1024 * 100]u8 = undefined;

export fn init() void {
    // var general_purpose_allocator = std.heap.GeneralPurposeAllocator(.{}){};
    // state.allocator = general_purpose_allocator.allocator();
    state.allocator = std.heap.c_allocator;

    sg.setup(.{
        .environment = sokol.glue.environment(),
        .logger = .{ .func = sokol.log.func },
    });

    state.renderer = Renderer.init();

    // setup sokol-fetch with 2 channels and 6 lanes per channel,
    // we'll use one channel for mesh data and the other for textures
    sokol.fetch.setup(.{
        .max_requests = 64,
        .num_channels = 1,
        .num_lanes = 1,
        .logger = .{ .func = sokol.log.func },
    });

    // start loading the base gltf file...
    _ = sokol.fetch.send(.{
        .path = "list_parts_basic.txt",
        .callback = fetch_callback_parts,
        .buffer = sokol.fetch.asRange(&fetch_buffer),
    });
}

export fn fetch_callback_parts(response: [*c]const sokol.fetch.Response) void {
    if (response.*.fetched) {
        const p: [*]const u8 = @ptrCast(response.*.data.ptr);
        const buf = p[0..response.*.data.size];
        // const allocator = std.heap.c_allocator;
        if (pmca_parts.parse(state.allocator, buf)) |list| {
            std.debug.print("{} parts\n", .{list.len});
            state.parts_list = list;

            _ = sokol.fetch.send(.{
                .path = "list_materials_basic.txt",
                .callback = fetch_callback_materials,
                .buffer = sokol.fetch.asRange(&fetch_buffer),
            });
        } else |_| {
            @panic("pmca_parts.parse");
        }
    } else if (response.*.failed) {
        @panic("fetch parts failed");
    }
}

export fn fetch_callback_materials(response: [*c]const sokol.fetch.Response) void {
    if (response.*.fetched) {
        const p: [*]const u8 = @ptrCast(response.*.data.ptr);
        const buf = p[0..response.*.data.size];
        if (pmca_material.parse(state.allocator, buf)) |list| {
            std.debug.print("{} materials\n", .{list.len});
            state.material_list = list;

            _ = sokol.fetch.send(.{
                .path = "list_transforms_basic.txt",
                .callback = fetch_callback_transforms,
                .buffer = sokol.fetch.asRange(&fetch_buffer),
            });
        } else |_| {
            @panic("pmca_material.parse");
        }
    } else if (response.*.failed) {
        @panic("fetch material failed");
    }
}

export fn fetch_callback_transforms(response: [*c]const sokol.fetch.Response) void {
    if (response.*.fetched) {
        const p: [*]const u8 = @ptrCast(response.*.data.ptr);
        const buf = p[0..response.*.data.size];
        if (pmca_transform.parse(state.allocator, buf)) |list| {
            std.debug.print("{} transforms\n", .{list.len});
            state.transform_list = list;

            _ = sokol.fetch.send(.{
                .path = "default.cnl",
                .callback = fetch_callback_cnl,
                .buffer = sokol.fetch.asRange(&fetch_buffer),
            });
        } else |_| {
            @panic("pmca_transform.parse");
        }
    } else if (response.*.failed) {
        @panic("fetch transform failed");
    }
}

export fn fetch_callback_cnl(response: [*c]const sokol.fetch.Response) void {
    if (response.*.fetched) {
        const p: [*]const u8 = @ptrCast(response.*.data.ptr);
        const buf = p[0..response.*.data.size];
        if (pmca_assembler.parse(state.allocator, buf)) |_assembler| {
            var assembler = _assembler;

            assembler.debug_print();

            const pmd = pmca_assembler.refresh(0, &assembler);
            state.renderer.loadModel(std.heap.c_allocator, @ptrCast(pmd)) catch
                @panic("loadModel");

            state.assembler = assembler;
        } else |_| {
            @panic("pmca_transform.parse");
        }
    } else if (response.*.failed) {
        @panic("fetch failed");
    }
}

export fn frame() void {
    sokol.fetch.dowork();

    state.input.screen_width = sokol.app.widthf();
    state.input.screen_height = sokol.app.heightf();
    state.orbit.frame(state.input);
    state.input.mouse_wheel = 0;
    const m = state.orbit.viewProjectionMatrix();

    {
        state.renderer.begin(sokol.glue.swapchain(), m);
        defer state.renderer.end();
        if (state.renderer.dsp) |dsp| {
            dsp.render();
        }
    }
    sg.commit();
}

export fn event(e: [*c]const sokol.app.Event) void {
    switch (e.*.type) {
        .MOUSE_DOWN => {
            switch (e.*.mouse_button) {
                .LEFT => {
                    state.input.mouse_left = true;
                },
                .RIGHT => {
                    state.input.mouse_right = true;
                },
                .MIDDLE => {
                    state.input.mouse_middle = true;
                },
                .INVALID => {},
            }
        },
        .MOUSE_UP => {
            switch (e.*.mouse_button) {
                .LEFT => {
                    state.input.mouse_left = false;
                },
                .RIGHT => {
                    state.input.mouse_right = false;
                },
                .MIDDLE => {
                    state.input.mouse_middle = false;
                },
                .INVALID => {},
            }
        },
        .MOUSE_MOVE => {
            state.input.mouse_x = e.*.mouse_x;
            state.input.mouse_y = e.*.mouse_y;
        },
        .MOUSE_SCROLL => {
            state.input.mouse_wheel = e.*.scroll_y;
        },
        else => {},
    }
}

export fn cleanup() void {
    sokol.fetch.shutdown();
    sg.shutdown();
}

pub fn main() void {
    sokol.app.run(.{
        .init_cb = init,
        .frame_cb = frame,
        .cleanup_cb = cleanup,
        .event_cb = event,
        .width = 2000,
        .height = 1200,
        .window_title = "pmcaz",
        .icon = .{ .sokol_default = true },
        .logger = .{ .func = sokol.log.func },
    });
}
