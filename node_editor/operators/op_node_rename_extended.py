from bpy.types import Context

from ...btypes import BOperator, BPoll
from ...keymap import register_keymap_item


class Preset:

    # def __call__(self, cls, context):
    #     print(self, cls, context)

    def __new__(
        cls,
    ):
        return classmethod(lambda cls, context: True)


@BOperator()
class SD_OT_node_rename_extended(BOperator.type):

    poll = BPoll.both(BPoll.is_node_editor, BPoll.is_active_node_tree)

    def draw(self, context: Context):
        layout = self.layout
        layout.prop()
        return

    def execute(self, context: Context):
        print("Hehehe")


register_keymap_item(SD_OT_node_rename_extended, key="F2")
