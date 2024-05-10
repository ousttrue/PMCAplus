import dataclasses
import logging
from OpenGL import GL
from glglue import glo
from glglue.camera.mouse_camera import MouseCamera
from glglue.drawable import Drawable, axes, grid
import glglue.frame_input


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PmdSrc:
    vertices: bytes
    indices: bytes
    submeshes: list[int]


PmdVS = """#version 330
in vec3 a_pos;
uniform mediump mat4 u_view;
uniform mediump mat4 u_projection;
uniform mediump mat4 u_model;

void main() {
  gl_Position = u_projection * u_view * u_model * vec4(a_pos, 1);  
}
"""

PmdFS = """#version 330
out vec4 FragColor;

void main() {
    FragColor = vec4(1, 1, 1, 1.0);
}
"""


class GlScene:
    def __init__(self) -> None:
        self.initialized = False
        self.mouse_camera = MouseCamera()
        self.drawables: list[Drawable] = []
        self.model_src: PmdSrc | None = None
        self.model_drawable: Drawable | None = None

    def lazy_initialize(self):
        if len(self.drawables) == 0:
            line_shader = glo.Shader.load_from_pkg("glglue", "assets/line")
            assert line_shader
            self.drawables.append(
                axes.create(
                    line_shader,
                    line_shader.create_props(self.mouse_camera.camera),
                )
            )
            self.drawables.append(
                grid.create(
                    line_shader,
                    line_shader.create_props(self.mouse_camera.camera),
                )
            )

        if not self.model_drawable:
            if self.model_src:
                shader = glo.shader.Shader.load(PmdVS, PmdFS)
                assert isinstance(shader, glo.shader.Shader)

                vbo = glo.Vbo()
                vbo.set_vertices(memoryview(self.model_src.vertices))

                ibo = glo.Ibo()
                ibo.set_bytes(self.model_src.indices, 2)

                pos = glo.AttributeLocation.create(shader.program, "a_pos")
                vao = glo.Vao(vbo, [glo.VertexLayout(pos, 3, 38, 0)], ibo)
                self.model_drawable = Drawable(vao)

                props = shader.create_props(self.mouse_camera.camera)
                for draw_count in self.model_src.submeshes:
                    self.model_drawable.push_submesh(shader, draw_count * 3, props)

                LOGGER.info("create mesh drawable")

    def set_model(self, src: PmdSrc) -> None:
        self.model_drawable = None
        self.model_src = src

    def render(self, frame: glglue.frame_input.FrameInput):
        self.lazy_initialize()

        # update camera
        self.mouse_camera.process(frame)

        # https://learnopengl.com/Advanced-OpenGL/Depth-testing
        GL.glEnable(GL.GL_DEPTH_TEST)  # type: ignore
        GL.glDepthFunc(GL.GL_LESS)  # type: ignore

        # https://learnopengl.com/Advanced-OpenGL/Face-culling
        # GL.glEnable(GL.GL_CULL_FACE)

        # clear
        GL.glViewport(0, 0, frame.width, frame.height)  # type: ignore
        if frame.height == 0:
            return
        GL.glClearColor(0, 0, 0, 1.0)  # type: ignore
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

        # render
        if self.model_drawable:
            self.model_drawable.draw()
        for drawable in self.drawables:
            drawable.draw()

        # flush
        GL.glFlush()
