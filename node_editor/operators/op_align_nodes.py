import bpy
from ...btypes import BOperator
from ...functions import vec_min, vec_max
from ...ui.ui_functions import dpifac
from mathutils import Vector as V


def get_input_nodes(node):
    nodes = set()
    for input in node.inputs:
        if input.links:
            for link in input.links:
                nodes.add(link.from_socket.node)
    return nodes


def get_bounding_box(node: bpy.types.Node):
    min = V((node.location.x, node.location.y - get_node_dims(node).y))
    max = V((node.location.x + node.width, node.location.y))
    nodes = get_input_nodes(node)
    for node in nodes:
        mi, ma = get_bounding_box(node)
        min = vec_min(mi, min)
        max = vec_max(ma, max)
    return min, max


def find_root_nodes(node):
    found = False
    roots = set()
    for node in get_input_nodes(node):
        roots |= find_root_nodes(node)
        found = True
    if not found:
        roots = {node}
    return roots


def get_node_tree(node):
    orig_node = node
    nodes = get_input_nodes(node)
    for node in nodes.copy():
        nodes |= get_node_tree(node)
    nodes.add(orig_node)
    return nodes


def move_node_tree(node, offset: V):
    for node in get_node_tree(node):
        node.location += offset


def get_node_dims(node):
    return node.dimensions / dpifac()


def organise_input_nodes(node):
    orig_node = node
    input_nodes = list(get_input_nodes(node))
    for i, node in enumerate(input_nodes):
        if i == 0:
            node.location.y = orig_node.location.y
        else:
            above_node = input_nodes[i - 1]
            node.location.y = above_node.location.y - get_node_dims(above_node).y - 20
        node.location.x = orig_node.location.x - (node.width + 20)
        organise_input_nodes(node)


@BOperator("strike")
class STRIKE_OT_align_nodes(BOperator.type):
    "Align the nodes in this node tree"

    @classmethod
    def poll(self, context):
        if not hasattr(context.space_data, "node_tree"):
            return True
        nt = context.space_data.node_tree
        return bool(nt)

    def execute(self, context):
        node = context.active_node
        organise_input_nodes(node)
        print(get_node_tree(node))