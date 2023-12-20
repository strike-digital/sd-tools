import os
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

import bpy
from bpy.props import IntProperty
from bpy.types import Area
from mathutils import Vector as V

from ..btypes import BOperator
from ..drawing import (
    DrawTexture,
    draw_rectangle,
    draw_text,
    get_text_dimensions,
    set_text_settings,
)
from ..handlers import DrawHandler
from ..math import Rectangle, vec_max, vec_min
from .prop_workspace_switcher import get_wswitcher_settings


@dataclass
class WorkspaceBox:
    name: str
    texture: DrawTexture = None
    position: V = V((0, 0))
    scale: float = 1

    @property
    def max(self):
        return self.position + (self.texture.dimensions * self.scale)


textures = {}


def safe_load_texture(file: Path):
    global textures
    if file in textures and textures[file].modified_time == os.path.getmtime(file):
        return textures[file]
    texture = DrawTexture(file)
    texture.modified_time = os.path.getmtime(file)
    textures[file] = texture
    return texture


@BOperator("strike")
class STRIKE_OT_switch_workspace(BOperator.type):
    index: IntProperty(default=1)

    def invoke(self, context, event):
        get_wswitcher_settings().set_access_time(context.workspace)
        self.workspace_names = [w.name for w in get_wswitcher_settings().ordered_workspace_list]

        area_sizes = {}
        for area in context.screen.areas:
            area_sizes[area] = area.width * area.height

        areas = [a for a in context.screen.areas]
        areas.sort(key=lambda a: area_sizes[a])
        self.area: Area = areas[-1]

        self.thumbnails_dir = Path(__file__).parent / "workspace_thumbnails"
        thumbnail_path = self.thumbnails_dir / f"{context.workspace.name}.png"
        bpy.ops.screen.screenshot(filepath=str(thumbnail_path))

        self.boxes: dict[str, WorkspaceBox] = OrderedDict()
        for name in self.workspace_names:
            self.boxes[name] = WorkspaceBox(name)

        global textures
        file = self.thumbnails_dir / "image_placeholder.png"
        default_texture = safe_load_texture(file)

        for name in self.workspace_names:
            file = self.thumbnails_dir / f"{name}.png"
            if file.exists():
                texture = safe_load_texture(file)
            else:
                texture = default_texture
            self.boxes[name].texture = texture

        self.handler = DrawHandler(self.draw_px, self.area.spaces.active, args=[context])
        self.area.tag_redraw()

        return self.start_modal()

    @property
    def current_name(self):
        return self.workspace_names[self.index]

    def finish(self):
        self.handler.remove()
        # for texture in set(b.texture for b in self.boxes.values()):
        #     texture.remove()
        return self.FINISHED

    def modal(self, context, event):
        self.area.tag_redraw()
        if event.type in {"ESC", "RIGHTMOUSE"}:
            return self.finish()

        if event.type == "LEFT_CTRL":
            return self.execute(context)
        if event.type == "TAB" and event.value == "PRESS":
            if event.shift:
                self.index -= 1
            else:
                self.index += 1
            self.index = self.index % len(self.workspace_names)
            return self.RUNNING_MODAL
        elif event.type == "LEFTMOUSE" and event.value == "PRESS":
            for box in self.boxes.values():
                rect = Rectangle(box.position, box.max)
                if rect.isinside(self.mouse_region):
                    self.index = self.workspace_names.index(box.name)
                    return self.execute(context)
        return self.RUNNING_MODAL

    def draw_px(self, context):
        if context.area != self.area:
            return

        box_height = 200
        out_padding = 100
        padding = 10
        region = next(r for r in self.area.regions if r.type == "WINDOW")
        maxx = region.width - padding
        minx = padding

        if context.preferences.system.use_region_overlap:
            space = self.area.spaces.active
            if self.area.type == "VIEW_3D":
                if hasattr(space, "show_region_ui") and space.show_region_ui:
                    region = next(r for r in self.area.regions if r.type == "UI")
                    maxx -= region.width

            if hasattr(space, "show_region_toolbar") and space.show_region_toolbar:
                region = next(r for r in self.area.regions if r.type == "TOOLS")
                minx += region.width

        # Calculate rows
        lines: list[list[WorkspaceBox]] = []
        line = []
        current_pos = V((minx, 0))
        for name, box in self.boxes.items():
            ratio = box_height / box.texture.height
            width = box.texture.width * ratio

            # If overflowing
            if current_pos.x + width > maxx:
                lines.append(line)
                current_pos.x = minx
                current_pos.y -= box_height + padding
                line = [box]
            else:
                line.append(box)

            box.position = current_pos.copy()
            box.scale = ratio
            current_pos.x += width + padding

        if line:
            lines.append(line)

        # fit all in frame
        maxy = lines[0][0].max.y + padding
        miny = lines[-1][-1].position.y
        size = maxy - miny

        region_height = region.height - padding * 2
        if size > region_height:
            for box in self.boxes.values():
                box.scale *= region_height / size
                box.position.y *= region_height / size

        # Center x
        for line in lines:
            box = line[-1]
            offset = (maxx - box.max.x) / 2
            for box in line:
                box.position.x += offset

        # Center y
        maxy = lines[0][0].max.y + padding
        miny = lines[-1][-1].position.y
        size = maxy - miny
        y_padding = (region.height - size) / 2
        offset = y_padding - miny
        for line in lines:
            for box in line:
                box.position.y += offset

        # Draw background
        min_co = V((10000, 10000))
        max_co = V((-10000, -100000))
        for box in self.boxes.values():
            min_co = vec_min(min_co, box.position)
            max_co = vec_max(max_co, box.max)

        padding_vector = V((padding, padding))
        draw_rectangle(Rectangle(min_co - padding_vector * 2, max_co + padding_vector * 2), [0, 0, 0, 0.8])

        highlight_color = [1, 1, 1, 0.7]

        # Draw
        for line in lines:
            for box in line:
                box.texture.draw(box.position, box.scale)

                text_padding = 10
                set_text_settings(box.position + V((text_padding, text_padding)), size=16, color=highlight_color)

                # Text background
                height = get_text_dimensions(box.name).y
                draw_rectangle(
                    Rectangle(box.position, V((box.max.x, box.position.y + height + text_padding * 1.5))),
                    color=(0, 0, 0, 0.7),
                )

                draw_text(box.name)

                if box.name == self.current_name:
                    tex_size = V((box.texture.width, box.texture.height))
                    rect = Rectangle(box.position, box.position + tex_size * box.scale)
                    draw_rectangle(rect, color=highlight_color, lines=True, thickness=2)

        # for i, name in enumerate(self.workspace_names):
        #     rect = Rectangle((100 * i, 100), (100 * i + 90, 200))
        #     draw_rectangle(rect)

        #     texture = self.textures[name]
        #     texture.draw(rect.min, scale=rect.height / texture.height)

        #     text_pos = rect.midpoint - get_text_dimensions(name) / 2
        #     set_text_settings(text_pos, 16)
        #     draw_text(name)

        #     if name == self.current_name:
        #         draw_rectangle(rect, lines=True, color=(1, 1, 1, 1))

    def execute(self, context):
        print(f"Going to {self.current_name}")
        context.window.workspace = bpy.data.workspaces[self.current_name]
        return self.finish()
