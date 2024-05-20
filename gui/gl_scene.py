from typing import Callable
import logging
from PySide6 import QtGui
from OpenGL import GL

from glglue import glo
from glglue.camera.mouse_camera import MouseCamera
from glglue.drawable import Drawable, axes, grid
import glglue.frame_input
from humanoidio import gltf


LOGGER = logging.getLogger(__name__)


def check_gl_error():
    while True:
        err = GL.glGetError()
        if err == GL.GL_NO_ERROR:
            break
        LOGGER.error(f"{err}")


def image_bytes(image: QtGui.QImage) -> bytes:
    match image.constBits():
        case bytes() as image_bytes:
            return image_bytes
        case bytearray() | memoryview() as data:
            return bytes(data)


def create_texture(image: QtGui.QImage) -> glo.Texture:
    match image.format():
        case QtGui.QImage.Format.Format_RGB32:
            image = image.convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
            texture = glo.Texture(
                image.width(),
                image.height(),
                image_bytes(image),
                pixel_type=GL.GL_RGBA,
            )
            return texture

        case QtGui.QImage.Format.Format_ARGB32_Premultiplied:  # alpha blend ?
            image = image.convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
            texture = glo.Texture(
                image.width(),
                image.height(),
                image_bytes(image),
                pixel_type=GL.GL_RGBA,
            )
            return texture

        case _ as f:
            raise RuntimeError(f)


class GlScene:
    def __init__(self) -> None:
        self.initialized = False
        self.mouse_camera = MouseCamera()
        self.drawables: list[Drawable] = []
        self.model_src: gltf.loader.Loader | None = None
        self.images: list[QtGui.QImage] = []
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
            LOGGER.info(GL.glGetString(GL.GL_VENDOR))
            LOGGER.info(GL.glGetString(GL.GL_RENDERER))
            LOGGER.info(GL.glGetString(GL.GL_VERSION))

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
                shader = glo.shader.Shader.load_from_pkg("glglue", "assets/mesh")
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
                            glo.AttributeLocation.create(shader.program, "a_normal"),
                            3,
                            32,
                            12,
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

                textures: list[glo.Texture] = [
                    create_texture(image) for image in self.images
                ]

                def get_texture_func(color_texture: int | None) -> Callable[[], None]:
                    if color_texture != None:
                        texture = textures[color_texture]

                        def set_texture():
                            u_texture.set_int(0)
                            GL.glActiveTexture(GL.GL_TEXTURE0)
                            texture.bind()

                        return set_texture

                    else:

                        def no_texture():
                            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

                        return no_texture

                for sm in mesh.submeshes:
                    material = self.model_src.materials[sm.material_index]

                    self.model_drawable.push_submesh(
                        shader,
                        sm.index_count,
                        props + [get_texture_func(material.color_texture)],
                    )

                LOGGER.info("create mesh drawable")

    def set_model(self, src: gltf.loader.Loader, images: list[QtGui.QImage]) -> None:
        self.model_drawable = None
        self.model_src = src
        self.images = images

    def render(self, frame: glglue.frame_input.FrameInput):
        self.lazy_initialize()

        # update camera
        self.mouse_camera.process(frame)

        # https://learnopengl.com/Advanced-OpenGL/Depth-testing
        GL.glEnable(GL.GL_DEPTH_TEST)  # type: ignore
        GL.glDepthFunc(GL.GL_LESS)  # type: ignore

        # https://learnopengl.com/Advanced-OpenGL/Face-culling
        GL.glEnable(GL.GL_CULL_FACE)

        # https://learnopengl.com/Advanced-OpenGL/Blending
        GL.glEnable(GL.GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        GL.glBlendFuncSeparate(
            GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA, GL.GL_ONE, GL.GL_ZERO
        )

        # clear
        GL.glViewport(0, 0, frame.width, frame.height)
        if frame.height == 0:
            return
        GL.glClearColor(*self.clear_color)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # render
        if self.model_drawable:
            self.model_drawable.draw()
        for drawable in self.drawables:
            drawable.draw()

        # flush
        GL.glFlush()
