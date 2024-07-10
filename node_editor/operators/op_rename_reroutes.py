from bpy.types import Node

from ...btypes import BOperator
from ...functions import get_active_node_tree


@BOperator()
class SD_OT_rename_reroutes(BOperator.type):

    @classmethod
    def poll(cls, context):
        if context.area.type != "NODE_EDITOR":
            return False

        nt = get_active_node_tree(context)
        if not nt:
            return False

        reroutes = {n for n in context.selected_nodes if n.type == "REROUTE"}
        return bool(reroutes)

    def get_connected_reroutes(self, reroute: Node):
        nodes = []
        node = reroute

        while True:
            if node.type != "REROUTE" or not node.inputs[0].links:
                break
            node = node.inputs[0].links[0].from_node
            nodes.append(node)

        return nodes

    def execute(self, context):
        nt = get_active_node_tree(context)
        reroutes = {n for n in context.selected_nodes if n.type == "REROUTE"}
        for reroute in reroutes:
            for connected_node in self.get_connected_reroutes(reroute):
                if connected_node.label:
                    reroute.label = connected_node.label
                    break
            else:
                reroute.label = connected_node.name
