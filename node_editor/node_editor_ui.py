import bpy
from bpy.types import Menu
from .operators.op_align_nodes_axis import STRIKE_OT_align_nodes_axis
from ..btypes import BMenu, BPanel


@BPanel(space_type="NODE_EDITOR", region_type="UI", label="Info", parent="NODE_PT_active_node_generic")
class STRIKE_PT_node_panel(bpy.types.Panel):

    @classmethod
    def poll(cls, context):
        if context.active_node:
            return True

    def draw(self, context):
        layout = self.layout
        node = context.active_node
        row = layout.row(align=True)
        row.operator("strike.align_nodes")
        row.scale_y = 2

        box = layout.column()
        box.use_property_split = True
        box.use_property_decorate = True
        # box.prop(node, "name", text="Name")
        # box.prop(node, "label", text="Label")
        box.prop(node, "type", text="Type")
        box.prop(node, "bl_idname", text="Id name")
        box.separator()
        box.prop(node, "dimensions")
        box.prop(node, "width", text="Width")
        box.prop(node, "height", text="Height")
        box.prop(node, "location", text="Location")
        box.separator()
        box.prop(node, "hide", toggle=True)
        box.prop(node, "use_custom_color", text="Use custom color", toggle=True)
        box.prop(node, "color", text="Color")
        if node.type == "FRAME":
            box.separator()
            box.prop(node, "label_size", text="Label size")
            box.prop(node, "shrink", text="Shrink to minimum", toggle=True)
            box.prop(node, "text")

        row = layout.row()
        row.scale_y = 1.5
        op = row.operator("wm.context_set_string", text="Copy data path", icon="FILE_SCRIPT")
        op.data_path = "window_manager.clipboard"
        op.value = ".".join([repr(node.id_data), node.path_from_id()])


@BMenu()
class STRIKE_MT_align_menu_pie(Menu):

    @classmethod
    def poll(cls, context):
        if not context.space_data or context.area.type != "NODE_EDITOR":
            return False
        return True

    def draw(self, context):
        layout = self.layout.menu_pie()
        op = layout.operator(STRIKE_OT_align_nodes_axis.bl_idname, text="Align nodes X")
        op.x = True
        op = layout.operator(STRIKE_OT_align_nodes_axis.bl_idname, text="Align nodes Y")
        op.x = False
