import bpy
from bpy.types import NodeSocket, UILayout

from ..btypes import BPanel
from ..settings.prop_window_manager import get_sd_settings


class SD_UL_inputs(bpy.types.UIList):
    inputs = True

    def draw_item(self, context, layout, data, socket: NodeSocket, icon, active_data, active_propname):
        layout: UILayout = layout
        row = layout.row(align=True)
        row.use_property_decorate = False
        row.prop(socket, "hide", text="", icon="HIDE_ON" if socket.hide else "HIDE_OFF", emboss=False)
        row.separator(factor=0.4)
        row.prop(socket, "name", text="", emboss=False)
        sub_row = row.row(align=True)
        sub_row.alignment = "RIGHT"
        idx = str(list(data.inputs if self.inputs else data.outputs).index(socket))
        sub_row.label(text=f"{idx}")


class SD_UL_outputs(bpy.types.UIList):
    inputs = False

    def draw_item(self, context, layout, data, socket: NodeSocket, icon, active_data, active_propname):
        SD_UL_inputs.draw_item(self, context, layout, data, socket, icon, active_data, active_propname)


@BPanel(space_type="NODE_EDITOR", region_type="UI", label="Info", parent="NODE_PT_active_node_generic")
class SD_PT_node_panel(bpy.types.Panel):
    @classmethod
    def poll(cls, context):
        if context.active_node:
            return True

    def draw(self, context):
        layout: UILayout = self.layout
        node = context.active_node
        sd = get_sd_settings(context)

        box = layout.box().column()

        # row = box.row()
        row = box.row(align=True)

        sub = row.row(align=True)
        show = sd.show_node_info
        sub.prop(
            sd,
            "show_node_info",
            icon="TRIA_DOWN" if show else "TRIA_RIGHT",
            text="Node",
            toggle=True,
            emboss=False,
        )
        sub = row.row(align=True)
        op = sub.operator("wm.context_set_string", text="", icon="COPYDOWN", emboss=False)
        op.data_path = "window_manager.clipboard"
        op.value = ".".join([repr(node.id_data), node.path_from_id()])

        if show:

            box.separator()

            col = box.column()
            col.use_property_split = True
            col.use_property_decorate = True
            col.prop(node, "type", text="Type")
            col.prop(node, "bl_idname", text="Id name")
            col.separator()
            col.prop(node, "dimensions")
            col.prop(node, "width", text="Width")
            col.prop(node, "height", text="Height")
            col.prop(node, "location", text="Location")
            col.separator()
            col.prop(node, "hide", toggle=True)
            col.prop(node, "use_custom_color", text="Use custom color", toggle=True)
            col.prop(node, "color", text="Color")
            if node.type == "FRAME":
                col.separator()
                col.prop(node, "label_size", text="Label size")
                col.prop(node, "shrink", text="Shrink to minimum", toggle=True)
                col.prop(node, "text")

        def draw_sockets(inputs: bool):
            box = layout.box().column()

            row: UILayout = box.row(align=True)
            show = sd.show_input_info if inputs else sd.show_output_info
            row.prop(
                sd,
                "show_input_info" if inputs else "show_output_info",
                icon="TRIA_DOWN" if show else "TRIA_RIGHT",
                text="Inputs      " if inputs else "Outputs      ",
                toggle=True,
                emboss=False,
            )

            if not show:
                return

            if inputs:
                box.template_list("SD_UL_inputs", "", node, "inputs", sd, "node_input_idx")
                socket = node.inputs[sd.node_input_idx]
            else:
                box.template_list("SD_UL_outputs", "", node, "outputs", sd, "node_output_idx")
                socket = node.outputs[sd.node_output_idx]

            box.separator()
            col = box.column()
            col.use_property_split = True
            col.use_property_decorate = True
            if hasattr(socket, "default_value"):
                col.prop(socket, "default_value", text="Value")
            col.prop(socket, "name", text="Display name")
            col.prop(socket, "identifier", text="Identifier")
            col.prop(socket, "bl_idname")
            col.prop(socket, "description", text="Description")
            col.prop(socket, "display_shape", text="Shape")
            col.prop(socket, "type")
            col.prop(socket, "enabled", text="Enabled")
            col.prop(socket, "hide", text="Hide")
            col.prop(socket, "hide_value", text="Hide value")
            col.prop(socket, "is_linked")

        if len(node.inputs):
            draw_sockets(inputs=True)

        if len(node.outputs):
            draw_sockets(inputs=False)
