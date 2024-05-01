from bpy.types import Context

from ...btypes import BOperator


@BOperator()
class SD_OT_extended_node_rename(BOperator.type):

    def execute(self, context: Context):
        return
