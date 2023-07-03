import bpy
from .general.operators.op_select_collection_objects import STRIKE_OT_select_collection_objects
from .general.operators.op_play_from_start import STRIKE_OT_play_from_start

addon_keymaps = []


def register():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Window")
    # insert keymap items here
    kmi = km.keymap_items.new(STRIKE_OT_play_from_start.bl_idname, type="SPACE", value="PRESS", shift=True)
    kmi = km.keymap_items.new(
        STRIKE_OT_select_collection_objects.bl_idname,
        type="LEFTMOUSE",
        value="PRESS",
        alt=True,
    )
    kmi = km.keymap_items.new(
        STRIKE_OT_select_collection_objects.bl_idname,
        type="LEFTMOUSE",
        value="PRESS",
        alt=True,
        shift=True,
    )
    kmi = km.keymap_items.new(
        STRIKE_OT_select_collection_objects.bl_idname,
        type="LEFTMOUSE",
        value="PRESS",
        alt=True,
        ctrl=True,
    )
    addon_keymaps.append(km)


def unregister():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()