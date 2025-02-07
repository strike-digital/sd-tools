from __future__ import annotations

from typing import Self

import bpy
from bpy.types import (
    Node,
    ShaderNodeBsdfPrincipled,
    ShaderNodeOutputMaterial,
    ShaderNodeTree,
    UILayout,
)

from ...btypes import BOperator


class DummyNode:
    node: Node = None
    children: list[DummyNode] = list()
    depth: int = 0
    default_depth = 10_000

    def __repr__(self):
        return f"Dummy({self.node})"

    def __init__(self, node: Node, depth: int = 0):
        self.node = node
        self.depth = depth
        self.children = []
        for input in self.node.inputs:
            if input.links:
                self.children.append(DummyNode(input.links[0].from_node, depth=depth + 1))

    def get_nearest_principled_node(self, depth) -> Self:
        if isinstance(self.node, ShaderNodeBsdfPrincipled):
            return self
        results = []
        for child in self.children:
            results.append(child.get_nearest_principled_node(depth + 1))

        return min(results, key=lambda n: n.depth)


@BOperator()
class SD_OT_auto_update_material_color(BOperator.type):
    """Update the material viewport display colors of every material in the scene, to match the color in the shader."""

    def get_main_color_node(node_tree: ShaderNodeTree):
        out_node = next((n for n in node_tree.nodes if isinstance(n, ShaderNodeOutputMaterial)), None)

        if not out_node:
            return

        dummy_out_node = DummyNode(node=out_node, depth=0)
        dummy_principled = dummy_out_node.get_nearest_principled_node(0)
        principled: Node = dummy_principled.node
        return principled

    def execute(self, context):
        for mat in bpy.data.materials:
            if not mat.node_tree:
                continue
            node = self.get_main_color_node(mat.node_tree)
            mat.diffuse_color = node.inputs[0].default_value


def menu_entry(self, context):
    layout: UILayout = self.layout
    SD_OT_auto_update_material_color.draw_button(layout)
    # layout.label(text="haha")


def register():
    bpy.types.MATERIAL_MT_context_menu.append(menu_entry)


def unregister():
    bpy.types.MATERIAL_MT_context_menu.remove(menu_entry)
