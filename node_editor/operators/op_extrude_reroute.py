import bpy
from bpy.types import NodeTree

from ...btypes import BOperator, ExecContext
from ...keymap import register_keymap_item


@BOperator()
class SD_OT_extrude_reroute(BOperator.type):

    @classmethod
    def poll(self, context):
        if not hasattr(context.space_data, "node_tree"):
            return False
        nt = context.space_data.node_tree
        if not nt:
            return False
        nodes = [n for n in nt.nodes if n.select and n.type == "REROUTE"]
        if not nodes:
            return False
        return True

    def execute(self, context):
        node_tree: NodeTree = context.space_data.node_tree
        nodes = node_tree.nodes

        reroutes = [n for n in node_tree.nodes if n.select and n.type == "REROUTE"]
        for from_node in reroutes:
            from_node.select = False
            to_node = nodes.new("NodeReroute")
            to_node.location = from_node.location
            node_tree.links.new(from_node.outputs[0], to_node.inputs[0])
            nodes.active = to_node
            # to_node.active = True

        bpy.ops.transform.translate(ExecContext.INVOKE, view2d_edge_pan=True)


register_keymap_item(SD_OT_extrude_reroute, key="E")
