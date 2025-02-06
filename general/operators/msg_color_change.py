from __future__ import annotations

from random import randint
from typing import Self

import bpy
from bpy.types import (
    Material,
    Node,
    ShaderNodeBsdfPrincipled,
    ShaderNodeOutputMaterial,
    ShaderNodeTree,
)

from .op_get_current_area import get_current_area


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


def get_material_from_node_tree(node_tree: ShaderNodeTree) -> Material:
    return next((m for m in bpy.data.materials if m.node_tree == node_tree), None)


def get_main_color_node(node_tree: ShaderNodeTree):
    out_node = next((n for n in node_tree.nodes if isinstance(n, ShaderNodeOutputMaterial)), None)

    if not out_node:
        return

    dummy_out_node = DummyNode(node=out_node, depth=0)
    dummy_principled = dummy_out_node.get_nearest_principled_node(0)
    principled: Node = dummy_principled.node
    return principled


def callback(*args):
    area = get_current_area()
    if not area:
        return
    if area.type != "NODE_EDITOR":
        area = next((a for a in bpy.context.screen.areas if a.type == "NODE_EDITOR"), None)
        print(area, randint(0, 10))
        if not area:
            return
    if area.spaces.active.shader_type != "OBJECT":
        return

    node_tree = area.spaces.active.node_tree
    if not node_tree or node_tree != area.spaces.active.edit_tree:
        return

    principled: Node = get_main_color_node(node_tree)

    color = principled.inputs[0].default_value
    material = get_material_from_node_tree(node_tree)
    material.diffuse_color = color


def driver_callback(material: Material, channel: int):
    node_tree = material.node_tree
    color_node = get_main_color_node(node_tree)
    return color_node.inputs[0].default_value[channel]


owner = object()
subscribe_to = (bpy.types.NodeSocketColor, "default_value")


def register():
    bpy.app.driver_namespace["copy_material_color"] = driver_callback
    # bpy.msgbus.subscribe_rna(
    #     key=subscribe_to,
    #     owner=owner,
    #     args=(),
    #     notify=callback,
    # )


def unregister():
    del bpy.app.driver_namespace["copy_material_color"]
    # bpy.msgbus.clear_by_owner(owner)
