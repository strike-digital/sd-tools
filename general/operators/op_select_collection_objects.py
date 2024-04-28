import bpy

from ...keymap import register_keymap_item

from ...btypes import BOperator


@BOperator("sd")
class SD_OT_select_collection_objects(BOperator.type):
    @classmethod
    def poll(cls, context):
        if context.area.type != "OUTLINER":
            return False
        return True

    def invoke(self, context, event):
        self.event = event
        return self.execute(context)

    def execute(self, context):
        bpy.ops.outliner.item_activate(
            "INVOKE_DEFAULT",
            deselect_all=True,
            extend=self.event.ctrl or self.event.shift,
        )
        if self.event.shift:
            bpy.ops.outliner.collection_objects_deselect("INVOKE_DEFAULT")
        else:
            bpy.ops.outliner.collection_objects_select("INVOKE_DEFAULT")


#  kmi = km.keymap_items.new(
#         SD_OT_select_collection_objects.bl_idname,
#         type="LEFTMOUSE",
#         value="PRESS",
#         alt=True,
#     )
#     kmi = km.keymap_items.new(
#         SD_OT_select_collection_objects.bl_idname,
#         type="LEFTMOUSE",
#         value="PRESS",
#         alt=True,
#         shift=True,
#     )
#     kmi = km.keymap_items.new(
#         SD_OT_select_collection_objects.bl_idname,
#         type="LEFTMOUSE",
#         value="PRESS",
#         alt=True,
#         ctrl=True,
#     )


register_keymap_item(SD_OT_select_collection_objects, key="LEFTMOUSE", alt=True)
register_keymap_item(SD_OT_select_collection_objects, key="LEFTMOUSE", alt=True, shift=True)
register_keymap_item(SD_OT_select_collection_objects, key="LEFTMOUSE", alt=True, ctrl=True)