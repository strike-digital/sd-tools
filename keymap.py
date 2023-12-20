import bpy

from .general.operators.op_play_from_start import STRIKE_OT_play_from_start
from .general.operators.op_select_collection_objects import (
    STRIKE_OT_select_collection_objects,
)
from .node_editor.node_editor_ui import STRIKE_MT_align_menu_pie
from .workspace_switcher.op_switch_workspace import STRIKE_OT_switch_workspace

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
    kmi = km.keymap_items.new(
        "wm.call_menu_pie",
        type="W",
        value="PRESS",
    )
    kmi.properties.name = STRIKE_MT_align_menu_pie.bl_idname
    kmi = km.keymap_items.new(
        STRIKE_OT_switch_workspace.bl_idname,
        type="TAB",
        value="PRESS",
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
