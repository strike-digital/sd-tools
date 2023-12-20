from pathlib import Path

import bpy
from bpy.props import IntProperty
from bpy.types import Area

from ..btypes import BOperator
from ..drawing import (
    DrawTexture,
    draw_rectangle,
    draw_text,
    get_text_dimensions,
    set_text_settings,
)
from ..handlers import DrawHandler
from ..math import Rectangle
from .prop_workspace_switcher import get_wswitcher_settings


@BOperator("strike")
class STRIKE_OT_switch_workspace(BOperator.type):
    index: IntProperty(default=1)

    def invoke(self, context, event):
        get_wswitcher_settings().set_access_time(context.workspace)
        self.workspace_names = [w.name for w in get_wswitcher_settings().ordered_workspace_list]

        area_sizes = {}
        for area in context.screen.areas:
            area_sizes[area] = area.width + area.height

        areas = [a for a in context.screen.areas]
        areas.sort(key=lambda a: area_sizes[a])
        self.area: Area = areas[-1]

        self.thumbnails_dir = Path(__file__).parent / "workspace_thumbnails"
        thumbnail_path = self.thumbnails_dir / f"{context.workspace.name}.png"
        bpy.ops.screen.screenshot(filepath=str(thumbnail_path))

        default_texture = DrawTexture(self.thumbnails_dir / "image_placeholder.png")
        self.textures: dict[str, DrawTexture] = {}
        for name in self.workspace_names:
            file = self.thumbnails_dir / f"{name}.png"
            if file.exists():
                texture = DrawTexture(file)
            else:
                texture = default_texture
            self.textures[name] = texture

        self.handler = DrawHandler(self.draw_px, area.spaces.active, args=[context])
        self.area.tag_redraw()
        print(self.area.type)

        return self.start_modal()

    @property
    def current_name(self):
        return self.workspace_names[self.index]

    def finish(self):
        self.handler.remove()
        for texture in set(self.textures.values()):
            texture.remove()
        return self.FINISHED

    def modal(self, context, event):
        self.area.tag_redraw()
        if event.type in {"ESC", "RIGHTMOUSE"}:
            print("Cancelled")
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
        return self.RUNNING_MODAL

    def draw_px(self, context):
        box_height = 100

        for i, name in enumerate(self.workspace_names):
            rect = Rectangle((100 * i, 100), (100 * i + 90, 200))
            draw_rectangle(rect)
            texture = self.textures[name]
            texture.draw(rect.min, scale=rect.height / texture.height)
            text_pos = rect.midpoint - get_text_dimensions(name) / 2
            set_text_settings(text_pos, 16)
            draw_text(name)

            if name == self.current_name:
                draw_rectangle(rect, lines=True, color=(1, 1, 1, 1))

    def execute(self, context):
        print(f"Going to {self.current_name}")
        context.window.workspace = bpy.data.workspaces[self.current_name]
        return self.finish()
