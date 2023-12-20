import bpy
import bpy.types as btypes

from ...btypes import BMenu
from .context_menu_ops import (
    SD_OT_collapse_group_input_nodes as collapse_group_inputs_op,
)
from .context_menu_ops import (
    SD_OT_connect_prop_to_group_input as connect_to_group_input_op,
)
from .context_menu_ops import (
    SD_OT_edit_group_socket_from_node as rename_group_socket_op,
)
from .context_menu_ops import SD_OT_extract_node_prop as extract_prop_op
from .context_menu_ops import (
    SD_OT_extract_node_prop_to_group_input as extract_prop_to_group_input_op,
)
from .context_menu_ops import (
    SD_OT_extract_node_prop_to_named_attr as extract_to_named_attr_op,
)
from .context_menu_ops import SD_OT_extract_node_to_group_input as extract_node_op
from .context_menu_ops import get_active_node_tree

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
class SD_MT_group_input_menu(btypes.Menu):
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


@BMenu(label="Extract to named attribute")
class SD_MT_named_attribute_menu(btypes.Menu):
    def draw(self, context: btypes.Context):
        nt = context.space_data.node_tree
        layout = self.layout

        def get_attrs(nodes):
            attrs = {}
            for node in nodes:
                if node.type == "GROUP" and node.node_tree:
                    attrs.update(get_attrs(node.node_tree.nodes))
                elif node.type == "INPUT_ATTRIBUTE":
                    if (socket := node.inputs[0].default_value) and not node.inputs[0].links:
                        attrs[socket] = node.data_type
                elif node.type == "STORE_NAMED_ATTRIBUTE":
                    if (socket := node.inputs[2].default_value) and not node.inputs[2].links:
                        attrs[socket] = node.data_type
            return attrs

        attrs = get_attrs(nt.nodes)

        if context.object:
            attrs.update({v.name: "FLOAT" for v in context.object.vertex_groups})

        op = layout.operator(extract_to_named_attr_op.bl_idname, text="New", icon="ADD")
        op.name = ""
        for attr, type in attrs.items():
            op = layout.operator(extract_to_named_attr_op.bl_idname, text=attr)
            op.name = attr
            op.type = type


def button_context_menu_draw(self, context):
    layout: btypes.UILayout = self.layout
    operators = [extract_prop_op, connect_to_group_input_op]
    for op in operators:
        if op.poll(context):
            layout.separator()
            break

    if extract_prop_op.poll(context):
        layout.operator(extract_prop_op.bl_idname, icon="NODE")

    if extract_to_named_attr_op.poll(context):
        layout.menu(SD_MT_named_attribute_menu.bl_idname, icon="NODE")

    if connect_to_group_input_op.poll(context):
        layout.menu(SD_MT_group_input_menu.bl_idname, icon="NODE")


def node_context_menu_draw(self, context):
    layout: btypes.UILayout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"

    operators = [extract_node_op, rename_group_socket_op, collapse_group_inputs_op]
    for op in operators:
        if op.poll(context):
            layout.separator()
            break

    operator = extract_node_op
    if operator.poll(context):
        layout.separator()
        layout.operator(operator.bl_idname, icon="NODE")
        # op = layout.operator(operator.bl_idname, text=operator.bl_label + " (without subtype)", icon="NODE")
        # op.with_subtype = False

    operator = rename_group_socket_op
    if operator.poll(context):
        layout.operator(operator.bl_idname, icon="NODE")

    operator = collapse_group_inputs_op
    if operator.poll(context):
        layout.operator(operator.bl_idname, icon="NODE")


def register():
    btypes.UI_MT_button_context_menu.append(button_context_menu_draw)
    btypes.NODE_MT_context_menu.append(node_context_menu_draw)


def unregister():
    btypes.UI_MT_button_context_menu.remove(button_context_menu_draw)
    btypes.NODE_MT_context_menu.remove(node_context_menu_draw)
