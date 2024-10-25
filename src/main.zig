//------------------------------------------------------------------------------
//  clear-sapp.c
//------------------------------------------------------------------------------
const sokol = @import("sokol");
const sg = sokol.gfx;
const pmca_parts = @import("pmca_parts.zig");

var pass_action = sg.PassAction{};

var fetch_buffer: [1024 * 100]u8 = undefined;

export fn init() void {
    sg.setup(.{
        .environment = sokol.glue.environment(),
        .logger = .{ .func = sokol.log.func },
    });
    pass_action.colors[0] = .{
        .load_action = .CLEAR,
        .clear_value = .{ .r = 1.0, .g = 0.0, .b = 0.0, .a = 1.0 },
    };

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
        .callback = parts_fetch_callback,
        .buffer = sokol.fetch.asRange(&fetch_buffer),
    });
}

export fn parts_fetch_callback(response: [*c]const sokol.fetch.Response) void {
    if (response.*.fetched) {
        // file has been loaded, parse as GLTF
        const p: [*]const u8 = @ptrCast(response.*.data.ptr);
        const buf = p[0..response.*.data.size];
        pmca_parts.parse(buf) catch @panic("parse");
    } else if (response.*.failed) {
        @panic("fetch failed");
    }
}

export fn frame() void {
    sokol.fetch.dowork();

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
