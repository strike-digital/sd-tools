from bpy.app import timers
from bpy.props import BoolProperty
from bpy.types import Context

from ...btypes import BOperator
from ...keymap import register_keymap_item


@BOperator(undo=True, dynamic_description=False)
class SD_OT_set_in_out_frame(BOperator.type):

    out: BoolProperty(
        name="Set out frame",
        default=False,
        description="Set the out frame rather than the in frame",
        options={"HIDDEN"},
    )

    @classmethod
    def poll(cls, context: Context):
        if not context.area:
            return False
        if context.area.type != "DOPESHEET_EDITOR":
            return False
        return True

    def execute(self, context):
        if self.out:
            context.scene.frame_end = context.scene.frame_current
        else:
            context.scene.frame_start = context.scene.frame_current


def start():
    props = register_keymap_item(SD_OT_set_in_out_frame, key="I", keymap_context="Window")
    props.out = False
    props = register_keymap_item(SD_OT_set_in_out_frame, key="O", keymap_context="Window")
    props.out = True


timers.register(start)

# props = register_keymap_item(SD_OT_set_in_out_frame, key="O", keymap_context="Window")
