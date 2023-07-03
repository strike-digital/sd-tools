from bpy.types import Context, AddonPreferences, NodeTree
from mathutils import Vector as V


def get_prefs(context: Context) -> AddonPreferences:
    """Get the addons preferences"""
    return context.preferences.addons[__package__].preferences


def vec_min(a, b) -> V:
    """Elementwise minimum for two vectors"""
    return V(min(e) for e in zip(a, b))


def vec_max(a, b) -> V:
    """Elementwise maximum for two vectors"""
    return V(max(e) for e in zip(a, b))


def get_active_node_tree(context) -> NodeTree:
    """Get the active node tree, taking node groups being edited into account"""
    return context.area.spaces.active.path[-1].node_tree


def get_active_area(screen, mouse_x, mouse_y):
    """Get the active area with only the mouse positions, useful when it is not given by the context"""
    for area in screen.areas:
        if area.x < mouse_x < area.x + area.width and area.y < mouse_y < area.y + area.height:
            return area