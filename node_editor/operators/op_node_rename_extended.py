from bpy.types import Context, Event

from ...btypes import BOperator, BPoll
from ...keymap import register_keymap_item


@BOperator()
class SD_OT_node_rename_extended(BOperator.type):

    poll = BPoll.both(BPoll.is_geometry_node_editor, BPoll.is_active_node_tree)

    def invoke(self, context: Context, event: Event):
        return self.call_popup()

    def draw(self, context: Context):
        layout = self.layout
        # layout.prop()
        return

    def execute(self, context: Context):
        print("Hehehe")


register_keymap_item(SD_OT_node_rename_extended, key="F2")
