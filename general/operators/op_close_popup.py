import bpy

from ...btypes import BOperator


@BOperator()
class SD_OT_close_popup(BOperator.type):
    """Close any open popup by briefly moving the mouse to the bottom corner of the screen."""

    # https://blender.stackexchange.com/a/202576/57981

    def execute(self, context):
        x, y = self.event.mouse_x, self.event.mouse_y
        context.window.cursor_warp(10, 10)

        move_back = lambda: context.window.cursor_warp(x, y)
        bpy.app.timers.register(move_back)
