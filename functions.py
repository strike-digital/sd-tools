from bpy.types import Context, AddonPreferences, NodeTree


def dump(obj, text):
    for attr in dir(obj):
        print(f"{repr(obj)}.{attr} = {getattr(obj, attr)}")


def get_prefs(context: Context) -> AddonPreferences:
    return context.preferences.addons[__package__].preferences



def get_active_node_tree(context) -> NodeTree:
    return context.area.spaces.active.path[-1].node_tree