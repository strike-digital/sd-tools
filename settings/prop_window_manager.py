import bpy
from bpy.props import IntProperty
from bpy.types import Context, PropertyGroup

from ..btypes import BPropertyGroup


@BPropertyGroup(bpy.types.WindowManager, "sd_tools")
class SDSettings(PropertyGroup):
    # The index of the input being viewed
    def get_idx(self, name: str):
        node = bpy.context.active_node
        return min(self.get(name, 0), len(node.inputs) - 1)

    def set_idx(self, name: str, value: int):
        self[name] = value

    def get_input_idx(self):
        return self.get_idx("_node_input_idx")

    def set_input_idx(self, value: int):
        self.set_idx("_node_input_idx", value)

    def get_output_idx(self):
        return self.get_idx("_node_output_idx")

    def set_output_idx(self, value: int):
        self.set_idx("_node_output_idx", value)

    node_input_idx: IntProperty(get=get_input_idx, set=set_input_idx)

    node_output_idx: IntProperty(get=get_output_idx, set=set_output_idx)

    show_node_info: bpy.props.BoolProperty(default=False)
    show_input_info: bpy.props.BoolProperty(default=False)
    show_output_info: bpy.props.BoolProperty(default=False)


def get_sd_settings(context: Context) -> SDSettings:
    return context.window_manager.sd_tools
