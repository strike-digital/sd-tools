import bpy
from .prop_workspace_switcher import get_wswitcher_settings
from ..btypes import BOperator


@BOperator("strike")
class STRIKE_OT_switch_workspace(BOperator.type):
    def invoke(self, context, event):
        self.current_index = 0
        self.workspace_names = [w.name for w in get_wswitcher_settings().ordered_workspace_list]
        return self.start_modal()

    @property
    def current_name(self):
        return self.workspace_names[self.current_index]

    def modal(self, context, event):
        if event.type in {"ESC", "RIGHTMOUSE"}:
            print("Cancelled")
            return self.FINISHED
        if event.type == "TAB" and event.value == "PRESS":
            if event.shift:
                self.current_index -= 1
            else:
                self.current_index += 1
                self.current_index = self.current_index % len(self.workspace_names)
            print(self.current_name)
            return self.RUNNING_MODAL
        return self.RUNNING_MODAL

    def execute(self, context):
        context.window.workspace = bpy.data.workspaces[self.current_name]
