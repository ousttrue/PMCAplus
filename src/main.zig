//------------------------------------------------------------------------------
//  clear-sapp.c
//------------------------------------------------------------------------------
const std = @import("std");
const sokol = @import("sokol");
const sg = sokol.gfx;
const pmca_parts = @import("pmca_parts.zig");
const pmca_material = @import("pmca_material.zig");
const pmca_transform = @import("pmca_transform.zig");
const pmca_assembler = @import("pmca_assembler.zig");

const state = struct {
    var allocator: std.mem.Allocator = undefined;
    var parts_list: []const pmca_parts.Parts = undefined;
    var material_list: []const pmca_material.Material = undefined;
    var transform_list: []const pmca_transform.Transform = undefined;
    var assembler: pmca_assembler.Assembler = undefined;
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
        if (pmca_assembler.parse(state.allocator, buf)) |assembler| {
            // std.debug.print("{} transforms\n", .{list.len});
            assembler.debug_print();

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

    var pass_action = sg.PassAction{};
    pass_action.colors[0] = .{
        .load_action = .CLEAR,
        .clear_value = .{ .r = 1.0, .g = 0.0, .b = 0.0, .a = 1.0 },
    };
    const g = pass_action.colors[0].clear_value.g + 0.01;
    pass_action.colors[0].clear_value.g = if (g > 1.0) 0.0 else g;
    sg.beginPass(.{
        .action = pass_action,
        .swapchain = sokol.glue.swapchain(),
    });
    sg.endPass();
    sg.commit();
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
        // .event_cb = __dbgui_event,
        .width = 400,
        .height = 300,
        .window_title = "Clear (sokol app)",
        .icon = .{ .sokol_default = true },
        .logger = .{ .func = sokol.log.func },
    });
}
