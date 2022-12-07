from bpy.types import Context, AddonPreferences, NodeTree
from mathutils import Vector as V


def dump(obj, text):
    for attr in dir(obj):
        print(f"{repr(obj)}.{attr} = {getattr(obj, attr)}")


def get_prefs(context: Context) -> AddonPreferences:
    return context.preferences.addons[__package__].preferences


def vec_min(a, b) -> V:
    """Elementwise minimum for two vectors"""
    return V(min(e) for e in zip(a, b))


def vec_max(a, b) -> V:
    """Elementwise maximum for two vectors"""
    return V(max(e) for e in zip(a, b))


def get_active_node_tree(context) -> NodeTree:
    return context.area.spaces.active.path[-1].node_tree