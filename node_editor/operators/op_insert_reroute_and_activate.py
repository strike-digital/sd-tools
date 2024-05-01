import bpy
from bpy.types import Context, Event

from ...btypes import BOperator, ExecContext
from ...keymap import register_keymap_item


@BOperator()
class SD_OT_insert_reroute_and_activate(BOperator.type):
    @classmethod
    def poll(cls, context):
        return bpy.ops.node.add_reroute.poll()

    def invoke(self, context: Context, event: Event):
        self.selected_nodes = context.selected_nodes
        self.finished = False
        bpy.ops.node.add_reroute(ExecContext.INVOKE.value)
        return self.start_modal()

    def modal(self, context: Context, event: Event):
        if self.finished:
            selected = context.selected_nodes
            if selected and selected != self.selected_nodes and selected[-1].type == "REROUTE":
                context.space_data.node_tree.nodes.active = selected[-1]
            return self.FINISHED

        if event.type in {"ESC"}:
            return self.FINISHED

        elif event.value == "RELEASE":
            self.finished = True
            return self.PASS_THROUGH

        return self.PASS_THROUGH


register_keymap_item(SD_OT_insert_reroute_and_activate, key="RIGHTMOUSE", shift=True)
