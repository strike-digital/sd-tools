from typing import Any

import bpy
import bpy.types as btypes
from bpy.props import StringProperty
from bpy.types import NodeTree

from ...bhelpers import BNodeTree
from ...btypes import BOperator
from ...functions import get_active_node_tree
from ...keymap import register_keymap_item

prop_names = {
    "FunctionNodeInputInt": "integer",
    "ShaderNodeValue": "default_value",
    "FunctionNodeInputVector": "vector",
    "GeometryNodeInputMaterial": "material",
    "FunctionNodeInputBool": "boolean",
    "FunctionNodeInputColor": "color",
    "GeometryNodeInputImage": "image",
    # "GeometryNodeObjectInfo": "",
    "FunctionNodeInputString": "string",
}


def split_camel_case(string: str):
    result = []
    last_upper = 0
    for i, c in enumerate(string):
        if c.isupper():
            result.append(string[last_upper:i])
            last_upper = i
    result.append(string[last_upper:])
    return result


def get_base_socket_type(socket: btypes.NodeSocket):
    """Remove the subtype from a socket idname (e.g. NodeSocketVector from NodeSocketVectorXYZ)"""
    val = "".join(split_camel_case(socket.bl_idname)[:4])
    return val


def hide_unused_outputs(node, exclude: set = ()):
    """If exclude, hide all outputs that are not in exclude, otherwise, hide all node outputs that have no links"""
    outputs = node.outputs
    exclude = {outputs[i] for i in exclude} or set()
    for i, output in enumerate(outputs):
        if exclude:
            output.hide = outputs[i] not in exclude
        else:
            if not output.links:
                output.hide = True


def get_modifier_input_names(m):
    keys = set()
    for k in m.keys():
        if not k.endswith("_attribute_name") and not k.endswith("_use_attribute") and k.startswith("Socket_"):
            keys.add(k)
    return keys


def get_modifier_inputs_dict(node_tree: NodeTree):
    # Create a dictionary containing the keys of all inputs in geo nodes modifiers for the current node tree
    # I really wish the devs would implement a sane system for interacting with geo nodes modifiers from the api
    # It would probably add a few more years on to the end of my life that have been stolen by the current system.
    modifiers = [
        m for obj in bpy.data.objects for m in obj.modifiers if m.type == "NODES" and m.node_group == node_tree
    ]

    inputs = {}
    for m in modifiers:
        inputs[m.name] = get_modifier_input_names(m)
    return inputs


def update_modifier_input_value(node_tree: NodeTree, inputs_dict: dict, value: Any):
    """Update the value of a new input in a geometry nodes modifier.
    Needs a previous inputs_dict created by `get_modifier_inputs_dict` to be able to find the new input."""
    if node_tree.type == "GEOMETRY":
        for obj in bpy.data.objects:
            for modifier in obj.modifiers:
                if modifier.type == "NODES" and modifier.node_group == node_tree:
                    # find the new key and change that property
                    keys = get_modifier_input_names(modifier)
                    keys.difference_update(inputs_dict[modifier.name])
                    new_key = list(keys)[0]
                    modifier[new_key] = value


@BOperator("sd", label="Extract to node", undo=True)
class SD_OT_extract_node_prop(BOperator.type):
    """Extract this value from a node into a separate input node"""

    types = {
        "INT": "FunctionNodeInputInt",
        "VALUE": "ShaderNodeValue",
        "BOOLEAN": "FunctionNodeInputBool",
        "VECTOR": "FunctionNodeInputVector",
        "STRING": "FunctionNodeInputString",
        "MATERIAL": "GeometryNodeInputMaterial",
        "RGBA": "FunctionNodeInputColor",
        "RGB": "FunctionNodeInputColor",
    }

    prop_names = prop_names

    @classmethod
    def poll(cls, context):
        if not hasattr(context, "button_pointer") or context.area.type != "NODE_EDITOR":
            return False

        node_tree = get_active_node_tree(context)
        if not node_tree:
            return False

        socket = context.button_pointer
        if not socket or not hasattr(socket, "is_output") or socket.is_output or socket.type not in cls.types:
            return False
        return True

    def execute(self, context: btypes.Context):
        socket: btypes.NodeSocket = context.button_pointer
        orig_node = socket.node
        value = socket.default_value
        # TODO make the value match when it is connected

        try:
            node_type = self.types[socket.type]
        except KeyError:
            self.report(
                {"WARNING"},
                "This socket type does not have an associated input node for the property to be extracted to",
            )
            return self.CANCELLED

        bpy.ops.node.add_node(
            "INVOKE_DEFAULT",
            type=node_type,
        )

        node = context.active_node
        node.label = socket.label if socket.label else socket.name
        node.location.x = orig_node.location.x - 20 - node.width
        node.location.y += 40

        bpy.ops.node.translate_attach("INVOKE_DEFAULT")

        output = node.outputs[0]
        if node.bl_idname == "ShaderNodeValue":
            output.default_value = value
        else:
            setattr(node, self.prop_names[node.bl_idname], value)
        node_tree = context.area.spaces.active.path[-1].node_tree
        node_tree.links.new(output, socket)


@BOperator("sd", label="Extract to named attribute", undo=True)
class SD_OT_extract_node_prop_to_named_attr(BOperator.type):
    """Extract this value to a named attribute"""

    types = {
        "INT": "INT",
        "VALUE": "FLOAT",
        "BOOLEAN": "BOOLEAN",
        "VECTOR": "FLOAT_VECTOR",
        "RGBA": "FLOAT_COLOR",
        "RGB": "FLOAT_COLOR",
    }

    prop_names = prop_names

    name: StringProperty()
    type: StringProperty()

    @classmethod
    def poll(cls, context):
        if not hasattr(context, "button_pointer") or context.area.type != "NODE_EDITOR":
            return False

        node_tree = get_active_node_tree(context)
        if not node_tree or node_tree.type != "GEOMETRY":
            return False

        socket = context.button_pointer
        if not socket or not hasattr(socket, "is_output") or socket.is_output or socket.type not in cls.types:
            return False
        return True

    def invoke(self, context: btypes.Context, event: btypes.Event):
        socket: btypes.NodeSocket = context.button_pointer
        orig_node = socket.node

        bpy.ops.node.add_node(
            "INVOKE_DEFAULT",
            type="GeometryNodeInputNamedAttribute",
        )

        node = context.active_node
        node.inputs[0].default_value = self.name
        self.node = node
        # node.label = socket.label if socket.label else socket.name
        node.location.x = orig_node.location.x - 20 - node.width
        node.location.y += 40
        node.data_type = self.type or self.types[socket.type]

        bpy.ops.node.translate_attach("INVOKE_DEFAULT")

        for output in node.outputs:
            if output.enabled:
                break
        # output = node.outputs[0]
        node_tree = context.area.spaces.active.path[-1].node_tree
        node_tree.links.new(output, socket)
        return self.FINISHED
        # return context.window_manager.invoke_props_popup(self, event)

    def draw(self, context: btypes.Context):
        layout = self.layout
        layout.activate_init = True
        row = layout.row()
        row.activate_init = True
        row.active_default = True
        context.active_node.inputs[0].draw(context, row, context.active_node, "hoho")
        # layout.prop(self.node.inputs[0], "default_value")
        # layout.template_node_view(context.space_data.node_tree, context.active_node, context.active_node.inputs[0])

    def execute(self, context: btypes.Context):
        return self.FINISHED


@BOperator("sd", label="Extract to new group input", undo=True)
class SD_OT_extract_node_prop_to_group_input(BOperator.type):
    """Extract this property as an input parameter for this node group"""

    @classmethod
    def poll(cls, context):
        if not hasattr(context, "button_pointer") or context.area.type != "NODE_EDITOR":
            return False

        node_tree = get_active_node_tree(context)
        if not node_tree:
            return False

        socket = context.button_pointer
        if not socket or not hasattr(socket, "is_output") or socket.is_output:
            return False
        return True

    def execute(self, context):
        socket: btypes.NodeSocket = context.button_pointer
        node_tree = get_active_node_tree(context)
        orig_node = socket.node
        if not (context.active_node and context.active_node.type == "GROUP_INPUT"):
            bpy.ops.node.add_node(
                "INVOKE_DEFAULT",
                type="NodeGroupInput",
            )
            bpy.ops.node.translate_attach("INVOKE_DEFAULT")
            node = context.active_node
            node.location.x = orig_node.location.x - 20 - node.width
            node.location.y += 40

        node = context.active_node
        node.label = socket.label if socket.label else socket.name

        # node_tree.inputs.new(type(socket).__name__, socket.name)
        # node_tree.interface.inputs
        # node_tree.interface.new_socket(socket_type=type(socket).__name__, name=socket.name)
        modifier_inputs = get_modifier_inputs_dict(node_tree)

        new_socket = node_tree.interface.new_socket(socket_type=get_base_socket_type(socket), name=socket.name)
        new_socket.from_socket(orig_node, socket)

        update_modifier_input_value(node_tree, modifier_inputs, socket.default_value)

        node_tree.links.new(node.outputs[new_socket.name], socket)
        hide_unused_outputs(node, exclude={-1, new_socket.name})

        for node in node_tree.nodes:
            if node.bl_idname == "NodeGroupInput":
                node.outputs[new_socket.name].hide = True


@BOperator("sd", label="Extract to group input", undo=True)
class SD_OT_extract_node_to_group_input(BOperator.type):
    """Extract this node as an input parameter for this node group"""

    types = {
        "FunctionNodeInputInt": "NodeSocketInt",
        "ShaderNodeValue": "NodeSocketFloat",
        "FunctionNodeInputVector": "NodeSocketVector",
        "GeometryNodeInputMaterial": "NodeSocketMaterial",
        "GeometryNodeInputImage": "NodeSocketImage",
        "FunctionNodeInputBool": "NodeSocketBool",
        "FunctionNodeInputColor": "NodeSocketColor",
        "FunctionNodeInputString": "NodeSocketString",
    }

    prop_names = prop_names

    with_subtype: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        if context.area.type != "NODE_EDITOR":
            return False

        node_tree = get_active_node_tree(context)
        if not node_tree:
            return False

        # Check to see whether this is a material or compositor, rather than a node group
        for ng in bpy.data.node_groups:
            if ng == node_tree:
                break
        else:
            return False

        if not node_tree.nodes.active or node_tree.nodes.active.bl_idname not in cls.types:
            return False
        return True

    def execute(self, context: btypes.Context):
        node_tree = get_active_node_tree(context)
        # node_tree: btypes.NodeTree = context.space_data.node_tree
        node: btypes.Node = context.active_node
        socket_name = node.label if node.label else node.name
        to_socket = []
        socket_type = self.types[node.bl_idname]
        node_type = getattr(bpy.types, node.bl_idname)
        matching = False

        # Get information from the socket the node is connected to rather than the node
        if node.outputs[0].links:
            link = node.outputs[0].links[0]
            to_sockets = [l.to_socket for l in node.outputs[0].links]
            to_socket = link.to_socket
            if not node.label:
                socket_name = to_socket.label if to_socket.label else to_socket.name
            if to_socket.type == link.from_socket.type:
                matching = True
                if self.with_subtype:
                    socket_type = to_socket.bl_idname

        modifier_inputs = get_modifier_inputs_dict(node_tree)

        # Add the new group input
        # socket = node_tree.inputs.new(socket_type, socket_name)
        # socket = node_tree.interface.new_socket(socket_name, socket_type=socket_type)
        socket = node_tree.interface.new_socket(socket_name, socket_type="NodeSocketVector")
        socket.from_socket(node, node.outputs[0])
        socket = node_tree.interface.items_tree[node_type.bl_rna.name]

        print(socket.name)
        socket_inputs = BNodeTree(node_tree).inputs
        if node.bl_idname == "ShaderNodeValue":
            value = node.outputs[0].default_value
        else:
            value = getattr(node, self.prop_names[node.bl_idname])
        socket.default_value = value
        # node_tree.active_input = len(socket_inputs) - 1
        node_tree.interface.active = socket

        # Set all occurrences of that property to the default value
        for ng in bpy.data.node_groups:
            for n in ng.nodes:
                if hasattr(n, "node_tree") and n.node_tree == node_tree:
                    socket_inputs[-1].default_value = value
                    pass

        # Do the same for modifiers if it is geometry nodes
        update_modifier_input_value(node_tree, modifier_inputs, value)

        # Set the min and max values if applicable
        if to_socket and matching:
            rna = to_socket.bl_rna.properties["default_value"]
            try:
                if hasattr(socket, "min_value") and not socket.default_value < rna.soft_min:
                    socket.min_value = rna.soft_min
                if hasattr(socket, "max_value") and not socket.default_value > rna.soft_min:
                    socket.max_value = rna.soft_max
            except TypeError:
                pass

        # Create a new group input node and replace the old node with it
        input_node = node_tree.nodes.new("NodeGroupInput")
        input_node.label = socket_name
        input_node.location = node.location
        for output in input_node.outputs[:-1]:
            if output.name != socket_name:
                output.hide = True

        # Hide the newly created socket from other input nodes
        for n in node_tree.nodes:
            if n.type == "GROUP_INPUT" and n != input_node:
                # shown = [o for o in n.outputs if not o.hide and not o.links]
                for o in n.outputs[:-1]:
                    if not o.links:
                        o.hide = True
                # if len(shown) <= 1:

        # Relink the new group input node
        if to_socket:
            for socket in to_sockets:
                node_tree.links.new(input_node.outputs[socket_name], socket)
        node_tree.nodes.active = input_node
        node_tree.nodes.remove(node)


@BOperator("sd", label="Connect to group input", undo=True)
class SD_OT_connect_prop_to_group_input(BOperator.type):
    """Connect this input to an existing group input"""

    input_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        if not hasattr(context, "button_pointer") or context.area.type != "NODE_EDITOR":
            return False

        node_tree = get_active_node_tree(context)
        if not node_tree:
            return False

        socket = context.button_pointer
        if not socket or not hasattr(socket, "is_output") or socket.is_output:
            return False
        return True

    def execute(self, context: btypes.Context):
        ng = get_active_node_tree(context)
        socket = context.button_pointer
        orig_node = socket.node
        nodes = ng.nodes
        links = ng.links

        # Use the active node if it is a group input, otherwise create a new one and use that
        if nodes.active and nodes.active.select and nodes.active.type == "GROUP_INPUT":
            node = nodes.active
        else:
            bpy.ops.node.add_node("INVOKE_DEFAULT", type="NodeGroupInput")
            node = context.active_node
            node.location.x = orig_node.location.x - 20 - node.width
            hide_unused_outputs(node, exclude={self.input_index, -1})
            bpy.ops.node.translate_attach_remove_on_cancel("INVOKE_DEFAULT")

        output = node.outputs[self.input_index]
        output.hide = False
        links.new(output, socket)


@BOperator("sd", label="Edit socket", undo=True)
class SD_OT_edit_group_socket_from_node(BOperator.type):
    """Edit the last linked socket of the currently selected group input/output"""

    @classmethod
    def poll(cls, context):
        if context.area.type != "NODE_EDITOR":
            return False

        node_tree = get_active_node_tree(context)
        if not node_tree:
            return False

        # Check to see whether this is a material or compositor, rather than a node group
        for ng in bpy.data.node_groups:
            if ng == node_tree:
                break
        else:
            return False

        node = node_tree.nodes.active
        if not node or node.bl_idname not in {"NodeGroupInput", "NodeGroupOutput"}:
            return False
        return True

    def invoke(self, context: btypes.Context, event):
        node_tree = BNodeTree(get_active_node_tree(context))
        node: btypes.Node = context.active_node
        is_group_input = node.bl_idname == "NodeGroupInput"
        self.is_group_input = is_group_input
        sockets = node.outputs if is_group_input else node.inputs
        nt_sockets = node_tree.inputs if is_group_input else node_tree.outputs
        for i, socket in enumerate(list(sockets)[::-1]):
            if socket.links and not socket.hide:
                self.socket = list(nt_sockets)[::-1][i - 1]
                return context.window_manager.invoke_popup(self)
        return self.FINISHED

    def draw(self, context):
        layout = self.layout
        layout.label(text="Rename socket:")
        socket: btypes.NodeTreeInterfaceSocket = self.socket
        layout.activate_init = True
        layout.prop(socket, "name", text="")

        # Taken directly from the node input panel draw script
        # Mimicking property split.
        layout.use_property_split = False
        layout.use_property_decorate = False
        layout_row = layout.row(align=True)
        layout_split = layout_row.split(factor=0.4, align=True)

        label_column = layout_split.column(align=True)
        label_column.alignment = "RIGHT"
        # Menu to change the socket type.
        label_column.label(text="Type")
        property_row = layout_split.row(align=True)

        property_row.prop(socket, "socket_type", text="")
        # op = property_row.operator_menu_enum(
        #     "node.tree_socket_change_type",
        #     "socket_type",
        #     text=socket.name if socket.name else socket.bl_socket_idname,
        # )
        # op.in_out = "IN" if self.is_group_input else "OUT"

        layout.use_property_split = True
        layout.use_property_decorate = False
        # layout.prop(socket, "name")
        # Display descriptions only for Geometry Nodes, since it's only used in the modifier panel.
        if get_active_node_tree(context).type == "GEOMETRY":
            layout.prop(socket, "description")
            field_socket_prefixes = {
                "NodeSocketInt",
                "NodeSocketColor",
                "NodeSocketVector",
                "NodeSocketBool",
                "NodeSocketFloat",
            }
            is_field_type = any(socket.bl_socket_idname.startswith(prefix) for prefix in field_socket_prefixes)
            if is_field_type:
                if not self.is_group_input:
                    layout.prop(socket, "attribute_domain")
                layout.prop(socket, "default_attribute_name")
        socket.draw(context, layout)


@BOperator("sd", label="Collapse unused inputs", undo=True)
class SD_OT_collapse_group_input_nodes(BOperator.type):
    """Hide all unused sockets from all of the group input nodes in this node tree"""

    @classmethod
    def poll(cls, context):
        if context.area.type != "NODE_EDITOR":
            return False

        node_tree = get_active_node_tree(context)
        if not node_tree:
            return False

        # Check to see whether this is a material or compositor, rather than a node group
        for ng in bpy.data.node_groups:
            if ng == node_tree:
                break
        else:
            return False
        return True

    def execute(self, context):
        node_tree = get_active_node_tree(context)
        selected_nodes = [n for n in context.selected_nodes if n.type == "GROUP_INPUT"]
        nodes = selected_nodes or node_tree.nodes

        for node in nodes:
            if node.bl_idname == "NodeGroupInput":
                hide_unused_outputs(node, exclude={-1})


register_keymap_item(SD_OT_collapse_group_input_nodes, key="H", alt=True)
