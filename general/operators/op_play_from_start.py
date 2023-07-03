import bpy
from bpy.types import Context, Operator
from ...btypes import BOperator


@BOperator("strike")
class STRIKE_OT_play_from_start(Operator):

    def execute(self, context: Context):

        context.scene.frame_set(context.scene.frame_start - 1)
        if not context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
        return {"FINISHED"}


# def register():


# def unregister():