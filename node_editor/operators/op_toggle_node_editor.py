import bpy
from bpy.types import KeyMap

from ...btypes import BOperator


@BOperator("sd")
class SD_OT_toggle_node_editor(BOperator.type):
    """Quickly switch between the geometry and shader node editors"""

    @classmethod
    def poll(cls, context):
        area = context.area
        if area.type != "NODE_EDITOR" and area.ui_type not in {"GeometryNodeTree", "ShaderNodeTree"}:
            return False
        return True

    def invoke(self, context, event):
        area = context.area
        area.ui_type = "ShaderNodeTree" if area.ui_type == "GeometryNodeTree" else "GeometryNodeTree"
        context.window_manager.modal_handler_add(self)
        return self.RUNNING_MODAL

    def modal(self, context, event):
        # This needs to be run in the modal function for the area ui_type to update
        if bpy.ops.node.view_selected.poll():
            bpy.ops.node.view_selected("INVOKE_DEFAULT")
        return self.FINISHED


addon_keymaps: list[KeyMap] = []


def register():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Window")
    addon_keymaps.append(km)

    km.keymap_items.new(
        idname=SD_OT_toggle_node_editor.bl_idname,
        type="BACK_SLASH",
        value="PRESS",
        shift=True,
    )


def unregister():
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
