import bpy
from bpy.types import Context

from ...btypes import BOperator
from ...keymap import register_keymap_item


@BOperator()
class SD_OT_play_from_start(BOperator.type):
    def execute(self, context: Context):
        context.scene.frame_set(context.scene.frame_start - 1)
        if not context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()


register_keymap_item(SD_OT_play_from_start, key="SPACE", shift=True)
