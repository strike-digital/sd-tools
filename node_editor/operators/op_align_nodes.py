import bpy
from ...btypes import BOperator


@BOperator("strike")
class STRIKE_OT_align_nodes(bpy.types.Operator):
    "Align the nodes in this node tree"

    @classmethod
    def poll(self, context):
        if not hasattr(context.space_data, "node_tree"):
            return True
        nt = context.space_data.node_tree
        return bool(nt)


    def execute(self, context):
        print("ha")

