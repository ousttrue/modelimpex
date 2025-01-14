import logging
from OpenGL import GL
from glglue.camera import MouseCamera
from glglue.drawable import Drawable
import glglue.frame_input
from glglue import glo
from glglue.drawable import cube, teapot, axes, grid
from . import rig


class SkeletonScene:
    def __init__(self) -> None:
        self.initialized = False
        self.roots: list[rig.BoneDict] = []
        self.mouse_camera = MouseCamera()
        self.drawables: list[Drawable] = []

    def render(self, frame: glglue.frame_input.FrameInput):
        self.begin_render(frame)
        self.draw()
        self.end_render()

    def draw(self):
        if not self.initialized:
            self.initialized = True

            # shader
            line_shader = glo.Shader.load_from_pkg("glglue", "assets/line")
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

        # render
        for drawable in self.drawables:
            drawable.draw()

    def begin_render(self, frame: glglue.frame_input.FrameInput):
        # update camera
        self.mouse_camera.process(frame)

        # https://learnopengl.com/Advanced-OpenGL/Depth-testing
        GL.glEnable(GL.GL_DEPTH_TEST)  # type: ignore
        GL.glDepthFunc(GL.GL_LESS)  # type: ignore

        # https://learnopengl.com/Advanced-OpenGL/Face-culling
        # GL.glEnable(GL.GL_CULL_FACE)

        # clear
        GL.glViewport(0, 0, frame.width, frame.height)  # type: ignore
        r = 0
        if frame.mouse_left:
            LOGGER.debug("LEFT_MOUSE")
            g = 0.1
        else:
            g = 0
        if frame.height == 0:
            return
        b = 0
        GL.glClearColor(r, g, b, 1.0)  # type: ignore
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

    def end_render(self):
        # flush
        GL.glFlush()
