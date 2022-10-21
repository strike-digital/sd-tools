import bpy
from ..helpers import BPanel


@BPanel(space_type="NODE_EDITOR", region_type="UI", label="Info", parent="NODE_PT_active_node_generic")
class STRIKE_PT_node_panel(bpy.types.Panel):

    @classmethod
    def poll(cls, context):
        if context.active_node:
            return True

    def draw(self, context):
        layout = self.layout
        node = context.active_node

        box1 = layout.box()
        box = box1.column()
        box.use_property_split = True
        box.use_property_decorate = True
        # box.prop(node, "name", text="Name")
        # box.prop(node, "label", text="Label")
        box.prop(node, "type", text="Type")
        box.prop(node, "bl_idname", text="Id name")
        box.prop(node, "dimensions")
        box.prop(node, "width", text="Width")
        box.prop(node, "height", text="Height")
        box.prop(node, "location", text="Location")
        box.prop(node, "hide", toggle=True)
        box.prop(node, "use_custom_color", text="Use custom color", toggle=True)
        box.prop(node, "color", text="Color")

        row = box1.row()
        row.scale_y = 1.5
        op = row.operator("wm.context_set_string", text="Copy data path", icon="FILE_SCRIPT")
        op.data_path = "window_manager.clipboard"
        op.value = ".".join([repr(node.id_data), node.path_from_id()])
