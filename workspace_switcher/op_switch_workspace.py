from ..btypes import BOperator


@BOperator("strike")
class STRIKE_OT_switch_workspace(BOperator.type):
    def invoke(self, context, event):
        
        return self.start_modal()

    def modal(self, context, event):
        if event.type in {"ESC", "RIGHTMOUSE"}:
            print("Cancelled")
            return self.FINISHED
        if event.type == "TAB" and event.value == "PRESS":
            print("hohoh")
            return self.RUNNING_MODAL
        return self.RUNNING_MODAL
