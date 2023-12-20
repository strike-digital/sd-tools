from __future__ import annotations

import time
from typing import Callable
from pathlib import Path

import blf

import bpy
import gpu
from gpu.types import GPUBatch, GPUShader
from mathutils import Vector as V
from gpu_extras.batch import batch_for_shader

from .math import Line, Rectangle, pad_list

textures: DrawTexture = []


class DrawTexture:
    """Helper class to represent a GPUTexture"""

    def __init__(self, path: Path):
        self.image = None
        self.on_update: list[Callable] = []
        self.update_texture(path)

    def update_texture(self, path: Path):
        if self.image:
            bpy.data.images.remove(self.image)

        name = f".{path.name}_{time.time()}"
        image = bpy.data.images.load(str(path), check_existing=False)
        image.name = name

        self.name = name
        self.image = image
        self.dimensions = V(image.size)
        self.texture = gpu.texture.from_image(image)
        textures.append(self)

        for func in self.on_update:
            func()

    @property
    def width(self):
        return self.dimensions.x

    @property
    def height(self):
        return self.dimensions.y

    def draw(self, position: V, scale: float):
        tex_coords = ((0, 0), (1, 0), (0, 1), (1, 1))
        coords = (
            (0, 0),
            (self.width, 0),
            (0, self.height),
            (self.width, self.height),
        )
        coords = [V(c) * scale + position for c in coords]
        indices = ((0, 1, 2), (2, 1, 3))
        shader = Shaders.image
        batch: GPUBatch = batch_for_shader(
            shader,
            "TRIS",
            {"pos": coords, "texCoord": tex_coords},
            indices=indices,
        )
        shader.uniform_sampler("image", self.texture)
        shader.bind()
        batch.draw(shader)

    def remove(self):
        textures.remove(self)
        bpy.data.images.remove(self.image)


class Shaders:
    if not bpy.app.background:
        _prefix = "" if bpy.app.version >= (4, 0, 0) else "2D_"
        uniform_color: GPUShader = gpu.shader.from_builtin(f"{_prefix}UNIFORM_COLOR")
        image: GPUShader = gpu.shader.from_builtin(f"{_prefix}IMAGE")


def draw_line(line: Line, color: V = V((1, 1, 1, 1)), thickness: float = 1.0):
    """Draw a line in the 2D viewport"""
    # Add alpha channel if necessary
    color = pad_list(color, 4, 1)

    shader = Shaders.uniform_color
    batch: GPUBatch = batch_for_shader(shader, "LINES", {"pos": list(line)})
    shader.uniform_float("color", [*color])
    gpu.state.line_width_set(thickness)
    shader.bind()
    batch.draw(shader)


def draw_rectangle(rectangle: Rectangle, color: V = V((1, 0, 1, 1)), lines=False, thickness: float = 1.0):
    # Add alpha channel if necessary
    color = pad_list(color, 4, 1)
    shader = Shaders.uniform_color
    gpu.state.blend_set("ALPHA")

    if lines:
        gpu.state.line_width_set(thickness)
        batch: GPUBatch = batch_for_shader(
            shader,
            "LINES",
            {"pos": rectangle.coords},
            indices=[
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 0),
            ],
        )
    else:
        batch: GPUBatch = batch_for_shader(shader, "TRIS", {"pos": rectangle.coords}, indices=rectangle.indices)
    shader.uniform_float("color", [*color])
    shader.bind()
    batch.draw(shader)


def set_text_settings(position: V = (0, 0), size: int = 1, color: V = (1, 1, 1, 1), fontid: int = 0):
    blf.size(fontid, size)
    blf.color(fontid, color[0], color[1], color[2], color[3])
    blf.position(fontid, position[0], position[1], 0)


def get_text_dimensions(text: str, fontid: int = 0):
    return V(blf.dimensions(fontid, text))


def draw_text(text: str, fontid: int = 0):
    blf.draw(fontid, text)


def unregister():
    for texture in textures:
        try:
            texture.remove()
        except ReferenceError:
            pass
