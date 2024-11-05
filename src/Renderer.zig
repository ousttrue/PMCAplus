const sokol = @import("sokol");
const sg = sokol.gfx;
pub const Renderer = @This();
const shader = @import("PMCA_view.glsl.zig");
const rowmath = @import("rowmath");
const glfw = @import("glfw_glue.zig");

pip: sg.Pipeline,

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

    return .{
        .pip = sg.makePipeline(pipDesc),
    };
}

pub fn begin(self: @This(), m: rowmath.Mat4) void {
    var action = sg.PassAction{};
    action.colors[0] = .{
        .load_action = .CLEAR,
        .clear_value = .{ .r = 0.1, .g = 0.1, .b = 0.1, .a = 1.0 },
    };

    sg.beginPass(.{
        .action = action,
        .swapchain = glfw.swapchain(),
    });

    sg.applyPipeline(self.pip);
    const vs_params = shader.VsParams{
        .mvp = m.m,
    };
    sg.applyUniforms(.VS, 0, sg.asRange(&vs_params));
}

pub fn end(_: @This()) void {
    defer sg.endPass();
}
