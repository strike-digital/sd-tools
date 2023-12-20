import bpy
from bpy.props import IntProperty
from bpy.types import Context, PropertyGroup

from ..btypes import BPropertyGroup


@BPropertyGroup(bpy.types.WindowManager, "sd_tools")
class SDSettings(PropertyGroup):
    # The index of the input being viewed
    def get_idx(self):
        node = bpy.context.active_node
        return min(self.get("_node_input_idx", 0), len(node.inputs) - 1)

    def set_idx(self, value: int):
        self["_node_input_idx"] = value

    node_input_idx: IntProperty(get=get_idx, set=set_idx)


def get_sd_settings(context: Context) -> SDSettings:
    return context.window_manager.sd_tools
