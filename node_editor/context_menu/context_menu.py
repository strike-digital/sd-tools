from re import A
import bpy.types as btypes
import bpy

from .context_menu_ops import (
    get_active_node_tree,
    STRIKE_OT_extract_node_prop as extract_prop_op,
    STRIKE_OT_extract_node_to_group_input as extract_node_op,
    STRIKE_OT_connect_prop_to_group_input as connect_to_group_input_op,
    STRIKE_OT_extract_node_prop_to_named_attr as extract_to_named_attr_op,
    STRIKE_OT_extract_node_prop_to_group_input as extract_prop_to_group_input_op,
)
from ...btypes import BMenu

compatible_with = {
    "GEOMETRY": {"GEOMETRY"},
    "STRING": set(),
    "SHADER": set(),
}

common_types = {"INT", "VECTOR", "RGBA", "RGB", "BOOLEAN", "VALUE"}
compatible_with |= {k: common_types for k in common_types}
compatible_with = {k: v | {k} for k, v in compatible_with.items()}
theme = bpy.context.preferences.themes[0].node_editor


@BMenu(label="Connect to group input")
class STRIKE_MT_group_input_menu(btypes.Menu):

    def draw(self, context: btypes.Context):
        ng = get_active_node_tree(context)
        layout: btypes.UILayout = self.layout
        orig_socket: btypes.NodeSocket = context.button_pointer

        layout.operator(extract_prop_to_group_input_op.bl_idname, text="New", icon="ADD")
        created = False
        for i, socket in enumerate(ng.inputs):
            if socket.type in compatible_with[orig_socket.type]:
                row = layout.row(align=True)
                op = row.operator(connect_to_group_input_op.bl_idname, text=socket.name)
                op.input_index = i
                created = True
        if not created:
            layout.label(text="No compatible group inputs")


def button_context_menu_draw(self, context):
    layout: btypes.UILayout = self.layout
    operators = [extract_prop_op, connect_to_group_input_op]
    for op in operators:
        if op.poll(context):
            layout.separator()

    if extract_prop_op.poll(context):
        layout.operator(extract_prop_op.bl_idname, icon="NODE")

    # if extract_prop_to_group_input_op.poll(context):
    # layout.operator(extract_prop_to_group_input_op.bl_idname, icon="NODE")

    if extract_to_named_attr_op.poll(context):
        layout.operator(extract_to_named_attr_op.bl_idname, icon="NODE")

    if connect_to_group_input_op.poll(context):
        layout.menu(STRIKE_MT_group_input_menu.bl_idname, icon="NODE")


def node_context_menu_draw(self, context):
    layout: btypes.UILayout = self.layout
    if extract_node_op.poll(context):
        layout.separator()
        operator = extract_node_op

        layout.operator(operator.bl_idname, icon="NODE")
        op = layout.operator(operator.bl_idname, text=operator.bl_label + " (without subtype)", icon="NODE")
        op.with_subtype = False


def register():
    btypes.UI_MT_button_context_menu.append(button_context_menu_draw)
    btypes.NODE_MT_context_menu.append(node_context_menu_draw)


def unregister():
    btypes.UI_MT_button_context_menu.remove(button_context_menu_draw)
    btypes.NODE_MT_context_menu.remove(node_context_menu_draw)