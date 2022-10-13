import bpy
from ..helpers import Op


@Op("strike", label="Extract property", undo=True)
class STRIKE_OT_extract_node_prop(bpy.types.Operator):
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

    @classmethod
    def poll(cls, context):
        if not hasattr(context, "button_pointer") or context.area.type != "NODE_EDITOR":
            return False
        if not context.space_data.node_tree:
            return False

        socket = context.button_pointer
        if not socket or not hasattr(socket, "is_output") or socket.is_output or socket.type not in cls.types:
            return False
        return True

    def execute(self, context: bpy.types.Context):
        socket: bpy.types.NodeSocket = context.button_pointer
        orig_node = socket.node
        value = socket.default_value

        try:
            node_type = self.types[socket.type]
        except KeyError:
            self.report(
                {"WARNING"},
                "This socket type does not have an associated input node for the property to be extracted to",
            )
            return {"FINISHED"}

        bpy.ops.node.add_node(
            "INVOKE_DEFAULT",
            type=node_type,
        )

        node = context.active_node
        node.location.x = orig_node.location.x - 20 - node.width
        node.location.y += 40

        bpy.ops.node.translate_attach("INVOKE_DEFAULT")

        output = node.outputs[0]
        node_tree = context.space_data.node_tree
        node_tree.links.new(output, socket)

        return {"FINISHED"}


@Op("strike", label="Extract as parameter", undo=True)
class STRIKE_OT_extract_node_to_parameter(bpy.types.Operator):
    """Extract this node as an input paramater for this node group"""

    types = {
        "FunctionNodeInputInt": "NodeSocketInt",
        "ShaderNodeValue": "NodeSocketFloat",
        "FunctionNodeInputVector": "NodeSocketVector",
        "GeometryNodeInputMaterial": "NodeSocketMaterial",
        "FunctionNodeInputBool": "NodeSocketBool",
        "FunctionNodeInputColor": "NodeSocketColor",
        # "GeometryNodeObjectInfo": "NodeSocketObject",
        "FunctionNodeInputString": "NodeSocketString",
    }

    prop_names = {
        "FunctionNodeInputInt": "integer",
        "ShaderNodeValue": "default_value",
        "FunctionNodeInputVector": "vector",
        "GeometryNodeInputMaterial": "material",
        "FunctionNodeInputBool": "boolean",
        "FunctionNodeInputColor": "color",
        # "GeometryNodeObjectInfo": "",
        "FunctionNodeInputString": "string",
    }

    with_subtype: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        if context.area.type != "NODE_EDITOR":
            return False
        node_tree = context.space_data.node_tree

        if not node_tree:
            return False

        # Check to see whether this is a material or compositor, rather than a node group
        for ng in bpy.data.node_groups:
            if ng == node_tree:
                break
        else:
            
            return False

        if not node_tree.nodes.active:
            return False
        return True

    def execute(self, context: bpy.types.Context):
        node_tree = context.space_data.node_tree
        node: bpy.types.Node = context.active_node
        name = node.label if node.label else node.name
        to_socket = None
        socket_type = self.types[node.bl_idname]
        matching = False

        if node.outputs[0].links:
            link = node.outputs[0].links[0]
            to_socket = link.to_socket
            name = to_socket.label if to_socket.label else to_socket.name
            if to_socket.type == link.from_socket.type:
                matching = True
                if self.with_subtype:
                    socket_type = to_socket.bl_idname

        socket = node_tree.inputs.new(socket_type, name)
        value = getattr(node, self.prop_names[node.bl_idname])
        if node.bl_idname == "ShaderNodeValue":
            value = node.outputs[0].default_value
        else:
            value = getattr(node, self.prop_names[node.bl_idname])
        socket.default_value = value
        node_tree.active_input = len(node_tree.inputs) - 1

        if to_socket and matching:
            rna = to_socket.bl_rna.properties["default_value"]
            if hasattr(socket, "min_value") and not socket.default_value < rna.soft_min:
                socket.min_value = rna.soft_min
            if hasattr(socket, "max_value") and not socket.default_value > rna.soft_min:
                socket.max_value = rna.soft_max
        print(context.active_node)
        return {"FINISHED"}


def button_context_menu_draw(self, context):
    layout: bpy.types.UILayout = self.layout
    if STRIKE_OT_extract_node_prop.poll(context):
        layout.separator()
        layout.operator(STRIKE_OT_extract_node_prop.bl_idname, icon="NODE")


def node_context_menu_draw(self, context):
    layout: bpy.types.UILayout = self.layout
    if STRIKE_OT_extract_node_to_parameter.poll(context):
        layout.separator()
        operator = STRIKE_OT_extract_node_to_parameter

        layout.operator(operator.bl_idname, icon="NODE")
        op = layout.operator(operator.bl_idname, text=operator.bl_label + " (without subtype)", icon="NODE")
        op.with_subtype = False


def register():
    bpy.types.UI_MT_button_context_menu.append(button_context_menu_draw)
    bpy.types.NODE_MT_context_menu.append(node_context_menu_draw)


def unregister():
    bpy.types.UI_MT_button_context_menu.remove(button_context_menu_draw)
    bpy.types.NODE_MT_context_menu.remove(node_context_menu_draw)