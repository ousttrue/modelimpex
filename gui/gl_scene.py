from typing import Callable
import pathlib
import logging
from PIL import Image
from OpenGL import GL
from glglue import glo
from glglue.camera.mouse_camera import MouseCamera
from glglue.drawable import Drawable, axes, grid
import glglue.frame_input
from humanoidio import gltf


LOGGER = logging.getLogger(__name__)


PmdVS = """#version 330
in vec3 a_pos;
in vec2 a_uv;
out vec2 v_uv;
uniform mediump mat4 u_view;
uniform mediump mat4 u_projection;
uniform mediump mat4 u_model;

void main() {
  float f = 1.58 / 20;
  gl_Position = u_projection * u_view * u_model * vec4(a_pos.x * f, a_pos.y * f, a_pos.z * f, 1);  
  v_uv = vec2(a_uv.x, a_uv.y);
}
"""


PmdFS = """#version 330
in vec2 v_uv;
out vec4 FragColor;
uniform sampler2D u_texture;

void main() {
    vec4 texel = texture(u_texture, v_uv);
    FragColor = texel;
    //FragColor = vec4(1, 1, 1, 1);
}
"""


def check_gl_error():
    while True:
        err = GL.glGetError()
        if err == GL.GL_NO_ERROR:
            break
        LOGGER.error(f"{err}")


def texture_func(
    src: pathlib.Path | gltf.Texture | None, uniform: glo.UniformLocation
) -> Callable[[], None]:
    LOGGER.debug(f"{src}")
    match src:
        case pathlib.Path():
            image = Image.open(src)  # type: ignore
            match image.mode:
                case "RGBA":
                    pixel_type = GL.GL_RGBA
                case "RGB":
                    pixel_type = GL.GL_RGB
                case _:
                    raise NotImplementedError()
            texture = glo.Texture(image.width, image.height, image.tobytes(), pixel_type=pixel_type)  # type: ignore

            def set_texture():
                uniform.set_int(0)
                GL.glActiveTexture(GL.GL_TEXTURE0)  # type: ignore
                texture.bind()

            return set_texture

        case gltf.Texture():
            raise NotImplementedError()

        case None:

            def no_texture():
                GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

            return no_texture


class GlScene:
    def __init__(self) -> None:
        self.initialized = False
        self.mouse_camera = MouseCamera()
        self.drawables: list[Drawable] = []
        self.model_src: gltf.loader.Loader | None = None
        self.model_drawable: Drawable | None = None
        self.is_shutdown = False
        self.clear_color = (0.3, 0.4, 0.5, 1)

    def shutdown(self) -> None:
        self.drawables.clear()
        self.model_drawable = None
        self.is_shutdown = True

    def lazy_initialize(self):
        if self.is_shutdown:
            return

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
                check_gl_error()

                mesh = self.model_src.meshes[0]

                vbo = glo.Vbo()
                vbo.set_vertices(memoryview(mesh.vertices))

                ibo = glo.Ibo()
                ibo.set_indices(mesh.indices)

                vao = glo.Vao(
                    vbo,
                    [
                        glo.VertexLayout(
                            glo.AttributeLocation.create(shader.program, "a_pos"),
                            3,
                            32,
                            0,
                        ),
                        glo.VertexLayout(
                            glo.AttributeLocation.create(shader.program, "a_uv"),
                            2,
                            32,
                            24,
                        ),
                    ],
                    ibo,
                )
                self.model_drawable = Drawable(vao)

                props = shader.create_props(self.mouse_camera.camera)
                u_texture = glo.UniformLocation.create(shader.program, "u_texture")

                for sm in mesh.submeshes:
                    material = self.model_src.materials[sm.material_index]
                    texture: pathlib.Path | gltf.Texture | None = None
                    if material.color_texture:
                        texture = self.model_src.textures[material.color_texture]
                    self.model_drawable.push_submesh(
                        shader,
                        sm.index_count,
                        props + [texture_func(texture, u_texture)],
                    )

                LOGGER.info("create mesh drawable")

    def set_model(self, src: gltf.loader.Loader) -> None:
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
        GL.glClearColor(*self.clear_color)  # type: ignore
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

        # render
        if self.model_drawable:
            self.model_drawable.draw()
        for drawable in self.drawables:
            drawable.draw()

        # flush
        GL.glFlush()
