import bpy
from bpy.types import Context, Image

from ...btypes import BOperator, ExecContext
from ...keymap import register_keymap_item


@BOperator("sd")
class SD_OT_render_in_new_slot(BOperator.type):
    """Render the scene, in a new render slot."""

    def execute(self, context: Context):
        render_image: Image = bpy.data.images.get("Render Result")
        if not render_image:
            return

        slots = render_image.render_slots
        if len(slots) == slots.active_index + 1:
            slot = slots[0]
            # slot = slots.new(name=f"Slot {len(slots)}")
        else:
            slot = slots[slots.active_index + 1]

        slots.active = slot

        bpy.ops.render.render(ExecContext.INVOKE.value)


register_keymap_item(SD_OT_render_in_new_slot, "F12")
