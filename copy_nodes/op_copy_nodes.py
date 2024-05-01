from bpy.types import Context

from ..btypes import BOperator
from ..keymap import register_keymap_item


@BOperator()
class SD_OT_copy_nodes(BOperator.type):

    @classmethod
    def poll(cls, context: Context):
        if not context.space_data or context.area.type != "NODE_EDITOR":
            return False
        if not context.selected_nodes:
            return False
        return True

    def execute(self, context: Context):
        print(context.selected_nodes)


register_keymap_item(SD_OT_copy_nodes, key="C", ctrl=True, shift=True)
