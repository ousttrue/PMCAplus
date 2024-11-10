const std = @import("std");
const sokol = @import("sokol");
const sg = sokol.gfx;
const ig = @import("cimgui");
const rowmath = @import("rowmath");
const InputState = rowmath.InputState;
const OrbitCamera = rowmath.OrbitCamera;
const pmca_parts = @import("pmca_parts.zig");
const pmca_material = @import("pmca_material.zig");
const pmca_transform = @import("pmca_transform.zig");
const pmca_assembler = @import("pmca_assembler.zig");
const Renderer = @import("Renderer.zig");
const font = @import("config").font;

const state = struct {
    var allocator: std.mem.Allocator = undefined;
    var parts_list: []const pmca_parts.Parts = undefined;
    var material_list: []const pmca_material.Material = undefined;
    var transform_list: []const pmca_transform.Transform = undefined;
    var assembler: ?pmca_assembler.Assembler = null;
    var renderer: Renderer = undefined;
    var input = InputState{};
    var orbit: OrbitCamera = .{
        .shift = .{ .x = 0, .y = 8, .z = 20 },
    };
    var flags = ig.ImGuiTableFlags_BordersV | ig.ImGuiTableFlags_BordersOuterH | ig.ImGuiTableFlags_Resizable | ig.ImGuiTableFlags_RowBg | ig.ImGuiTableFlags_NoBordersInBody;
    var tree_node_flags = ig.ImGuiTreeNodeFlags_SpanAllColumns;
};

// Simple storage to output a dummy file-system.
const MyTreeNode = struct {
    Name: []const u8,
    Type: []const u8,
    Size: c_int,
    ChildIdx: usize,
    ChildCount: usize,

    fn DisplayNode(node: *const MyTreeNode, all_nodes: []const MyTreeNode) void {
        ig.igTableNextRow(0, 0);
        _ = ig.igTableNextColumn();
        const is_folder = (node.ChildCount > 0);
        if (is_folder) {
            const open = ig.igTreeNodeEx_Str(&node.Name[0], state.tree_node_flags);
            _ = ig.igTableNextColumn();
            ig.igTextDisabled("--");
            _ = ig.igTableNextColumn();
            ig.igTextUnformatted(&node.Type[0], 0);
            if (open) {
                for (0..node.ChildCount) |child_n| {
                    DisplayNode(&all_nodes[node.ChildIdx + child_n], all_nodes);
                }
                ig.igTreePop();
            }
        } else {
            _ = ig.igTreeNodeEx_Str(&node.Name[0], state.tree_node_flags | ig.ImGuiTreeNodeFlags_Leaf | ig.ImGuiTreeNodeFlags_Bullet | ig.ImGuiTreeNodeFlags_NoTreePushOnOpen);
            _ = ig.igTableNextColumn();
            ig.igText("%d", node.Size);
            _ = ig.igTableNextColumn();
            ig.igTextUnformatted(&node.Type[0], 0);
        }
    }
    const nodes = [_]MyTreeNode{
        .{ .Name = "Root", .Type = "Folder", .Size = -1, .ChildIdx = 1, .ChildCount = 3 }, // 0
        .{ .Name = "Music", .Type = "Folder", .Size = -1, .ChildIdx = 4, .ChildCount = 2 }, // 1
        .{ .Name = "Textures", .Type = "Folder", .Size = -1, .ChildIdx = 6, .ChildCount = 3 }, // 2
        .{ .Name = "desktop.ini", .Type = "System file", .Size = 1024, .ChildIdx = 0, .ChildCount = 0 }, // 3
        .{ .Name = "File1_a.wav", .Type = "Audio file", .Size = 123000, .ChildIdx = 0, .ChildCount = 0 }, // 4
        .{ .Name = "File1_b.wav", .Type = "Audio file", .Size = 456000, .ChildIdx = 0, .ChildCount = 0 }, // 5
        .{ .Name = "Image001.png", .Type = "Image file", .Size = 203128, .ChildIdx = 0, .ChildCount = 0 }, // 6
        .{ .Name = "Copy of Image001.png", .Type = "Image file", .Size = 203256, .ChildIdx = 0, .ChildCount = 0 }, // 7
        .{ .Name = "Copy of Image001 (Final2).png", .Type = "Image file", .Size = 203512, .ChildIdx = 0, .ChildCount = 0 }, // 8
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
    sokol.imgui.setup(.{
        .logger = .{
            .func = sokol.log.func,
        },
        .no_default_font = true,
    });

    const io = ig.igGetIO();
    const config = ig.ImFontConfig_ImFontConfig();
    defer ig.ImFontConfig_destroy(config);
    config.*.FontDataOwnedByAtlas = false;
    config.*.OversampleH = 2;
    config.*.OversampleV = 2;
    config.*.RasterizerMultiply = 2;
    // _ = ig.ImFontAtlas_AddFontDefault(io.*.Fonts, null);
    // config.*.MergeMode = true;
    // _ = ig.ImFontAtlas_AddFontFromFileTTF(
    //     io.*.Fonts,
    //     "C:/Windows/Fonts/MSGothic.ttc",
    //     18,
    //     null,
    //     ig.ImFontAtlas_GetGlyphRangesJapanese(io.*.Fonts),
    // );
    _ = ig.ImFontAtlas_AddFontFromMemoryTTF(
        io.*.Fonts,
        @ptrCast(@constCast(&font[0])),
        font.len,
        18,
        null,
        ig.ImFontAtlas_GetGlyphRangesJapanese(io.*.Fonts),
    );
    // https://github.com/floooh/sokol-samples/pull/135/files
    sokol.imgui.createFontsTexture(.{});

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

pub fn inputFromScreen() InputState {
    const io = ig.igGetIO().*;
    var input = InputState{
        .screen_width = io.DisplaySize.x,
        .screen_height = io.DisplaySize.y,
        .mouse_x = io.MousePos.x,
        .mouse_y = io.MousePos.y,
    };
    if (!io.WantCaptureMouse) {
        input.mouse_left = io.MouseDown[ig.ImGuiMouseButton_Left];
        input.mouse_right = io.MouseDown[ig.ImGuiMouseButton_Right];
        input.mouse_middle = io.MouseDown[ig.ImGuiMouseButton_Middle];
        input.mouse_wheel = io.MouseWheel;
    }
    return input;
}

export fn frame() void {
    sokol.fetch.dowork();

    sokol.imgui.newFrame(.{
        .width = sokol.app.width(),
        .height = sokol.app.height(),
        .delta_time = sokol.app.frameDuration(),
        .dpi_scale = sokol.app.dpiScale(),
    });

    //=== UI CODE STARTS HERE
    _ = ig.igShowDemoWindow(null);

    // {
    //     ig.igSetNextWindowPos(.{ .x = 10, .y = 10 }, ig.ImGuiCond_Once, .{ .x = 0, .y = 0 });
    //     ig.igSetNextWindowSize(.{ .x = 400, .y = 100 }, ig.ImGuiCond_Once);
    //     _ = ig.igBegin("PMCA", 0, ig.ImGuiWindowFlags_None);
    //     defer ig.igEnd();
    //
    //     _ = ig.igColorEdit3(
    //         "Background",
    //         &state.renderer.pass_action.colors[0].clear_value.r,
    //         ig.ImGuiColorEditFlags_None,
    //     );
    // }

    var TEXT_BASE: ig.ImVec2 = undefined;
    ig.igCalcTextSize(&TEXT_BASE, "A", null, false, 0);
    // const TEXT_BASE_HEIGHT = ig.igGetTextLineHeightWithSpacing();

    // if (ig.igTreeNode_Str("Tree view")) {
    //     _ = ig.igCheckboxFlags_IntPtr("ImGuiTreeNodeFlags_SpanFullWidth", &state.tree_node_flags, ig.ImGuiTreeNodeFlags_SpanFullWidth);
    //     _ = ig.igCheckboxFlags_IntPtr("ImGuiTreeNodeFlags_SpanTextWidth", &state.tree_node_flags, ig.ImGuiTreeNodeFlags_SpanTextWidth);
    //     _ = ig.igCheckboxFlags_IntPtr("ImGuiTreeNodeFlags_SpanAllColumns", &state.tree_node_flags, ig.ImGuiTreeNodeFlags_SpanAllColumns);
    //     //     HelpMarker("See \"Columns flags\" section to configure how indentation is applied to individual columns.");

    if (state.assembler) |assembler| {
        pmca_assembler.beginTable(TEXT_BASE.x);
        defer ig.igEndTable();

        pmca_assembler.displayNode(.{
            .nodes = assembler.nodes.items,
            .node_path = pmca_assembler.NodePath.init(),
        }, 0);
    }
    //=== UI CODE ENDS HERE

    state.input = inputFromScreen();
    state.orbit.frame(state.input);
    state.input.mouse_wheel = 0;
    const m = state.orbit.viewProjectionMatrix();

    {
        state.renderer.begin(sokol.glue.swapchain(), m);
        defer state.renderer.end();
        if (state.renderer.dsp) |dsp| {
            dsp.render();
        }
        sokol.imgui.render();
    }
    sg.commit();
}

export fn event(e: [*c]const sokol.app.Event) void {
    _ = sokol.imgui.handleEvent(e.*);
}

export fn cleanup() void {
    sokol.fetch.shutdown();
    sokol.imgui.shutdown();
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
