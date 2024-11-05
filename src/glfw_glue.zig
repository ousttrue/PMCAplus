const std = @import("std");
const sokol = @import("sokol");
const sg = sokol.gfx;
const c = @cImport({
    @cInclude("GLFW/glfw3.h");
});

const state = struct {
    var _sample_count: i32 = 0;
    var _no_depth_buffer = false;
    var _major_version: i32 = 0;
    var _minor_version: i32 = 0;
    var _window: *c.GLFWwindow = undefined;
};

pub const GlfwDesc = struct {
    width: i32,
    height: i32,
    sample_count: i32 = 1,
    no_depth_buffer: bool,
    title: [*:0]const u8,
    version_major: i32 = 4,
    version_minor: i32 = 1,
};

pub fn init(desc_def: GlfwDesc) void {
    std.debug.assert(desc_def.width > 0);
    std.debug.assert(desc_def.height > 0);
    state._sample_count = desc_def.sample_count;
    state._no_depth_buffer = desc_def.no_depth_buffer;
    state._major_version = desc_def.version_major;
    state._minor_version = desc_def.version_minor;
    _ = c.glfwInit();
    c.glfwWindowHint(c.GLFW_COCOA_RETINA_FRAMEBUFFER, 0);
    if (desc_def.no_depth_buffer) {
        c.glfwWindowHint(c.GLFW_DEPTH_BITS, 0);
        c.glfwWindowHint(c.GLFW_STENCIL_BITS, 0);
    }
    c.glfwWindowHint(c.GLFW_SAMPLES, if (desc_def.sample_count == 1)
        0
    else
        desc_def.sample_count);
    c.glfwWindowHint(c.GLFW_CONTEXT_VERSION_MAJOR, desc_def.version_major);
    c.glfwWindowHint(c.GLFW_CONTEXT_VERSION_MINOR, desc_def.version_minor);
    c.glfwWindowHint(c.GLFW_OPENGL_FORWARD_COMPAT, c.GLFW_TRUE);
    c.glfwWindowHint(c.GLFW_OPENGL_PROFILE, c.GLFW_OPENGL_CORE_PROFILE);
    state._window = c.glfwCreateWindow(
        desc_def.width,
        desc_def.height,
        desc_def.title,
        null,
        null,
    ) orelse {
        @panic("glfwCreateWindow");
    };
    c.glfwMakeContextCurrent(state._window);
    c.glfwSwapInterval(1);
}

pub fn shutdown() void {
    c.glfwTerminate();
}

pub fn isRunning() bool {
    return c.glfwWindowShouldClose(state._window) == 0;
}

pub fn flush() void {
    c.glfwSwapBuffers(state._window);
    c.glfwPollEvents();
}

pub fn environment() sg.Environment {
    return .{
        .defaults = .{
            .color_format = .RGBA8,
            .depth_format = if (state._no_depth_buffer) .NONE else .DEPTH_STENCIL,
            .sample_count = state._sample_count,
        },
    };
}

pub fn swapchain() sg.Swapchain {
    var width: i32 = undefined;
    var height: i32 = undefined;
    c.glfwGetFramebufferSize(state._window, &width, &height);
    return .{
        .width = width,
        .height = height,
        .sample_count = state._sample_count,
        .color_format = .RGBA8,
        .depth_format = if (state._no_depth_buffer) .NONE else .DEPTH_STENCIL,
        .gl = .{
            // we just assume here that the GL framebuffer is always 0
            .framebuffer = 0,
        },
    };
}
