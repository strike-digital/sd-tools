import bpy
from bpy.types import Menu, UILayout

from ..btypes import BMenu, BPanel
from ..settings.prop_window_manager import get_strike_settings
from .operators.op_align_nodes_axis import STRIKE_OT_align_nodes_axis


class STRIKE_UL_inputs(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout: UILayout = layout
        layout.prop(item, "name", text="", emboss=False)
        row = layout.row(align=True)
        row.alignment = "RIGHT"
        idx = str(list(data.inputs).index(item))
        row.label(text=f"{idx}")


@BPanel(space_type="NODE_EDITOR", region_type="UI", label="Info", parent="NODE_PT_active_node_generic")
class STRIKE_PT_node_panel(bpy.types.Panel):
    @classmethod
    def poll(cls, context):
        if context.active_node:
            return True

    def draw(self, context):
        layout = self.layout
        node = context.active_node

        box = layout.box().column()
        box.use_property_split = True
        box.use_property_decorate = True

        # row = box.row()
        row = box.row(align=True)

        sub = row.row(align=True)
        sub.alignment = "CENTER"
        sub.label(text="       Node")

        sub = row.row(align=True)
        op = sub.operator("wm.context_set_string", text="", icon="COPYDOWN", emboss=False)
        op.data_path = "window_manager.clipboard"
        op.value = ".".join([repr(node.id_data), node.path_from_id()])

        box.separator()

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

        box = layout.box().column()
        box.use_property_split = True
        box.use_property_decorate = True

        row = box.row(align=True)
        row.alignment = "CENTER"
        row.label(text="Inputs")

        strike = get_strike_settings(context)
        box.template_list("STRIKE_UL_inputs", "", node, "inputs", strike, "node_input_idx")
        socket = node.inputs[strike.node_input_idx]

        box.separator()
        if hasattr(socket, "default_value"):
            box.prop(socket, "default_value", text="Value")
        box.prop(socket, "name", text="Display name")
        box.prop(socket, "identifier", text="Identifier")
        box.prop(socket, "bl_idname")
        box.prop(socket, "description", text="Description")
        box.prop(socket, "display_shape", text="Shape")
        box.prop(socket, "type")
        box.prop(socket, "enabled", text="Enabled")
        box.prop(socket, "hide", text="Hide")
        box.prop(socket, "hide_value", text="Hide value")
        box.prop(socket, "is_linked")


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
