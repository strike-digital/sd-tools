import bpy
from bpy.types import Context, Event

from ...btypes import BOperator, ExecContext


@BOperator("sd")
class SD_OT_insert_reroute_and_select(BOperator.type):
    @classmethod
    def poll(cls, context):
        return bpy.ops.node.add_reroute.poll()

    def invoke(self, context: Context, event: Event):
        self.selected_nodes = context.selected_nodes
        self.finished = False
        print(self.selected_nodes)
        bpy.ops.node.add_reroute(ExecContext.INVOKE.value)
        return self.start_modal()

    def modal(self, context: Context, event: Event):
        print("Modal!")
        if self.finished:
            selected = context.selected_nodes
            if selected and selected != self.selected_nodes and selected[-1].type == "REROUTE":
                context.space_data.node_tree.nodes.active = selected[-1]
            return self.FINISHED

        if event.type in {"ESC"}:
            return self.FINISHED

        elif event.value == "RELEASE":
            print("FINISHED")
            self.finished = True
            return self.PASS_THROUGH

        return self.PASS_THROUGH
