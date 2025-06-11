from statistics import mean

from bpy.props import BoolProperty
from bpy.types import Menu
from mathutils import Vector as V

from ...btypes import BMenu, BOperator
from ...keymap import register_keymap_item


def snap_to_grid(value: V):
    return V((round(value.x / 20) * 20, round(value.y / 20) * 20))


@BOperator(undo=True)
class SD_OT_align_nodes_axis(BOperator.type):
    x: BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        if not context.space_data or context.area.type != "NODE_EDITOR":
            return False
        nodes: list = context.selected_nodes
        if len(nodes) <= 1:
            return False
        return True

    def execute(self, context):
        nodes = context.selected_nodes
        mean_location = V((mean(n.location.x for n in nodes), mean(n.location.y for n in nodes)))
        mean_location = snap_to_grid(mean_location)
        for node in nodes:
            if self.x:
                node.location.x = mean_location.x
            else:
                node.location.y = mean_location.y


@BOperator(undo=True)
class SD_OT_space_nodes(BOperator.type):
    x: BoolProperty(default=True)

    reverse: BoolProperty()

    @classmethod
    def poll(cls, context):
        if not context.space_data or context.area.type != "NODE_EDITOR":
            return False
        nodes: list = context.selected_nodes
        if len(nodes) <= 1:
            return False
        return True

    def execute(self, context):
        nodes: list = context.selected_nodes
        nodes.sort(key=lambda n: n.location.x if self.x else n.location.y, reverse=self.reverse)
        if self.reverse:
            position = V(nodes[0].location)
        else:
            position = V(nodes[0].location + nodes[0].dimensions)
        for node in nodes[1:]:
            if self.reverse:
                position -= node.dimensions + V((20, 20))
            else:
                position += V((20, 20))

            position = snap_to_grid(position)

            # if self.x:
            node.location.x = position.x
            # else:
            #     node.location.y = position.y

            if not self.reverse:
                position += node.dimensions


@BMenu()
class SD_MT_align_menu_pie(Menu):
    @classmethod
    def poll(cls, context):
        if not context.space_data or context.area.type != "NODE_EDITOR":
            return False
        return True

    def draw(self, context):
        layout = self.layout.menu_pie()
        op = layout.operator(SD_OT_space_nodes.bl_idname, text="Space nodes left")
        op.reverse = False
        op = layout.operator(SD_OT_space_nodes.bl_idname, text="Space nodes right")
        op.reverse = True
        op = layout.operator(SD_OT_align_nodes_axis.bl_idname, text="Align nodes X")
        op.x = True
        op = layout.operator(SD_OT_align_nodes_axis.bl_idname, text="Align nodes Y")
        op.x = False


properties = register_keymap_item("wm.call_menu_pie", key="Q", alt=True)
properties.name = SD_MT_align_menu_pie.bl_idname
