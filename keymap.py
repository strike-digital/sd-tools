from typing import TypeVar, Union

import bpy
from bpy.types import KeyMap, KeyMapItem, KeyMapItems

from .btypes import BOperatorBase

addon_keymaps = []
km: KeyMap = None


T = TypeVar("T", bound=BOperatorBase)


def register_keymap_item(
    operator: Union[T, str],
    key: str,
    value: str = "PRESS",
    shift: bool = False,
    ctrl: bool = False,
    alt: bool = False,
    oskey: bool = False,
) -> Union[T, KeyMapItem]:
    """Create a new keymap item.
    Returns the new keymap item properties, which can be used to set the properties that the operator can be called with
    """
    global km
    if not km:
        addon = bpy.context.window_manager.keyconfigs.addon
        km = addon.keymaps.new(name="Window")
    idname = operator if isinstance(operator, str) else operator.bl_idname

    keymap_items: KeyMapItems = km.keymap_items
    kmi = keymap_items.new(idname=idname, type=key, value=value, shift=shift, ctrl=ctrl, alt=alt, oskey=oskey)
    addon_keymaps.append((km))
    return kmi.properties


def unregister():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
