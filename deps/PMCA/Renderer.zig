const std = @import("std");
const sokol = @import("sokol");
const sg = sokol.gfx;
pub const Renderer = @This();
const shader = @import("PMCA_view.glsl.zig");
const rowmath = @import("rowmath");
const c = @cImport({
    @cInclude("mlib_PMD_rw01.h");
});

const Vertex = struct {
    loc: [3]f32,
    // nom: [3]f32,
    uv: [2]f32,
};

const Submesh = struct {
    draw_count: u32 = 0,
};

pub const DspModel = struct {
    bind: sg.Bindings = .{},
    materials: [128]Submesh = undefined,
    material_count: u32 = 0,
    index_count: u32 = 0,

    pub fn deinit(self: *@This()) void {
        sg.destroyBuffer(self.bind.vertex_buffers[0]);
        sg.destroyBuffer(self.bind.index_buffer);
    }

    pub fn render(self: @This()) void {
        sg.applyBindings(self.bind);
        // var offset: u32 = 0;
        // for (self.materials) |material| {
        //     sg.draw(offset, material.draw_count, 1);
        //     offset += material.draw_count;
        // }
        sg.draw(0, self.index_count, 1);
    }
};

pip: sg.Pipeline,
pass_action: sg.PassAction = .{},
dsp: ?DspModel = null,

pub fn init() @This() {
    // a shader
    const shd = sg.makeShader(shader.pmcaViewShaderDesc(sg.queryBackend()));

    // a pipeline state object (default render states are fine for triangle)
    var pipDesc = sg.PipelineDesc{
        .shader = shd,
        .index_type = .UINT16,
        .depth = .{
            .compare = .LESS,
            .write_enabled = true,
        },
        .cull_mode = .BACK,
    };
    pipDesc.layout.buffers[0].stride = 20;
    pipDesc.layout.attrs[0].format = .FLOAT3;
    pipDesc.layout.attrs[0].buffer_index = 0;
    pipDesc.layout.attrs[1].format = .FLOAT2;
    pipDesc.layout.attrs[1].buffer_index = 0;

    var renderer = Renderer{
        .pip = sg.makePipeline(pipDesc),
    };
    renderer.pass_action.colors[0] = .{
        .load_action = .CLEAR,
        .clear_value = .{ .r = 1.0, .g = 0.0, .b = 0.0, .a = 1.0 },
    };
    return renderer;
}

pub fn begin(
    self: *@This(),
    swapchain: sg.Swapchain,
    m: rowmath.Mat4,
) void {
    sg.beginPass(.{
        .action = self.pass_action,
        .swapchain = swapchain,
    });
    sg.applyPipeline(self.pip);
    const vs_params = shader.VsParams{
        .mvp = m.m,
    };
    sg.applyUniforms(0, sg.asRange(&vs_params));
}

pub fn end(_: @This()) void {
    defer sg.endPass();
}

pub fn loadModel(
    self: *@This(),
    allocator: std.mem.Allocator,
    model: *c.MODEL,
) !void {
    if (self.dsp) |*dsp| {
        dsp.deinit();
    }

    var dsp = DspModel{};

    var vertices = try allocator.alloc(Vertex, model.vt_count);
    defer allocator.free(vertices);
    for (0..model.vt_count) |i| {
        const src = model.vt[i];
        vertices[i] = .{
            .loc = .{
                src.loc[0],
                src.loc[1],
                -src.loc[2],
            },
            // .nom = model.vt[i].nor,
            .uv = src.uv,
        };
    }
    const vbuf = sg.makeBuffer(.{ .data = sg.asRange(vertices) });
    dsp.bind.vertex_buffers[0] = vbuf;

    const ibuf = sg.makeBuffer(.{
        .type = .INDEXBUFFER,
        .data = .{
            .ptr = model.vt_index,
            .size = 2 * model.vt_index_count,
        },
    });
    dsp.bind.index_buffer = ibuf;
    dsp.index_count = model.vt_index_count;

    for (0..model.mat_count) |i| {
        dsp.materials[i].draw_count = model.mat[i].vt_index_count;
    }
    dsp.material_count = model.mat_count;

    self.dsp = dsp;
}
