from bpy.props import BoolProperty, StringProperty
from bpy.types import Context, Event, Node, UILayout

from ...btypes import BOperator, BPoll, ExecContext
from ...general.operators.op_close_popup import SD_OT_close_popup
from ...keymap import register_keymap_item


@BOperator()
class SD_OT_node_rename_extended(BOperator.type):

    show_settings: BoolProperty(default=False)
    show_properties: BoolProperty(default=True)
    show_group: BoolProperty(default=True)

    def label_update(self, context: Context):
        node = context.space_data.edit_tree.nodes.active
        if node.label != self.node_label:
            SD_OT_close_popup.run(ExecContext.INVOKE)
        node.label = self.node_label
        pass

    node_label: StringProperty(update=label_update)

    @classmethod
    def poll(cls, context: Context):
        if not BPoll.poll_active_node_tree(context):
            return False

        node = context.space_data.edit_tree.nodes.active
        return bool(node)

    def invoke(self, context: Context, event: Event):
        self.node = context.space_data.edit_tree.nodes.active
        self.node_label = self.node.label
        return self.call_popup()

    def draw_header(self, layout: UILayout, show_name: str, label: str):
        row = layout.row()
        show = getattr(self, show_name)
        row.prop(
            self,
            show_name,
            text=f"{label}               ",
            toggle=True,
            emboss=False,
            icon="DOWNARROW_HLT" if show else "RIGHTARROW",
        )
        return show

    def draw(self, context: Context):
        layout = self.layout
        layout = layout.column(align=True)
        tree = context.space_data.edit_tree
        node: Node = tree.nodes.active

        row = layout.row()
        row.scale_y = 1.5
        row.alignment = "CENTER"
        row.label(text=node.label or node.name)
        layout.separator(factor=0.6)

        layout.activate_init = True
        # layout.prop(node, "label", text="", icon="NODE", placeholder="Node Label")
        layout.prop(self, "node_label", text="", icon="NODE", placeholder="Node Label")

        layout.separator(factor=2.2)
        box = layout.box()

        if self.draw_header(box, "show_settings", "Settings"):
            box.prop(node, "name", text="Name", icon="NODE")
            row = box.row(align=True)
            row.label(text="Color:")
            row.prop(
                node,
                "use_custom_color",
                text="",
                toggle=True,
                icon="CHECKBOX_HLT" if node.use_custom_color else "CHECKBOX_DEHLT",
            )
            subrow = row.row(align=True)
            subrow.active = node.use_custom_color
            subrow.prop(node, "color", text="")
            subrow.popover(panel="NODE_PT_node_color_presets", text="", icon="PRESET")

        box = layout.box()
        if self.draw_header(box, "show_properties", "Properties"):
            node.draw_buttons_ext(context, box)

        # Group settings
        if node.type != "GROUP" or not node.node_tree:
            return

        box = layout.box()
        if self.draw_header(box, "show_group", "Group"):
            layout = box
            tree = node.node_tree

            split = layout.row()
            split.template_node_tree_interface(tree.interface)

            ops_col = split.column(align=True)
            ops_col.operator_menu_enum("node.interface_item_new", "item_type", icon="ADD", text="")
            ops_col.operator("node.interface_item_remove", icon="REMOVE", text="")
            ops_col.separator()
            ops_col.menu("NODE_MT_node_tree_interface_context_menu", icon="DOWNARROW_HLT", text="")

            ops_col.separator()

            active_item = tree.interface.active
            if active_item is not None:
                layout.use_property_split = True
                layout.use_property_decorate = False

                if active_item.item_type == "SOCKET":
                    layout.prop(active_item, "socket_type", text="Type")
                    layout.prop(active_item, "description")
                    # Display descriptions only for Geometry Nodes, since it's only used in the modifier panel.
                    if tree.type == "GEOMETRY":
                        field_socket_types = {
                            "NodeSocketInt",
                            "NodeSocketColor",
                            "NodeSocketVector",
                            "NodeSocketBool",
                            "NodeSocketFloat",
                        }
                        if active_item.socket_type in field_socket_types:
                            if "OUTPUT" in active_item.in_out:
                                layout.prop(active_item, "attribute_domain")
                            layout.prop(active_item, "default_attribute_name")
                    if hasattr(active_item, "draw"):
                        active_item.draw(context, layout)

                if active_item.item_type == "PANEL":
                    layout.prop(active_item, "description")
                    layout.prop(active_item, "default_closed", text="Closed by Default")

                layout.use_property_split = False


register_keymap_item(SD_OT_node_rename_extended, key="F2")
