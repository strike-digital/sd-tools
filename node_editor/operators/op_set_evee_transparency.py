import bpy
from bpy.types import Context
from ...btypes import BOperator


@BOperator("strike")
class STRIKE_OT_set_eevee_transparency(BOperator.type):

    @classmethod
    def poll(cls, context):
        if context.area.type != "NODE_EDITOR":
            return False
        if context.space_data.tree_type != "ShaderNodeTree":
            return False
        if not context.space_data.node_tree:
            return False
        return True

    def execute(self, context: Context):
        nt = context.space_data.node_tree
        for mat in bpy.data.materials:
            if mat.node_tree == nt:
                break
        else:
            print("Can't get material")
            return

        mat.blend_method = "CLIP"
        mat.shadow_method = "CLIP"
