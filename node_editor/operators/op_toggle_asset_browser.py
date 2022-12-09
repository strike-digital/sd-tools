import bpy
from ...btypes import BOperator

opened_area = None


@BOperator("strike")
class STRIKE_OT_toggle_asset_browser(bpy.types.Operator):

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global opened_area
        areas = {a for a in context.screen.areas}
        area = context.area
        # area = opened_area if opened_area else context.area
        with context.temp_override(area=area):
            # # if opened_area:
            # #     # bpy.ops.screen.area_close()
            # #     a = opened_area
            # #     # bpy.ops.screen.area_dupli()
            # #     # bpy.ops.wm
            # #     # bpy.ops.screen.area_join(cursor=(opened_area.x + 2, opened_area.y + 3))
            # #     bpy.ops.screen.area_join(cursor=(a.x, a.y + a.width))
            # #     opened_area = None
            # #     return {"FINISHED"}
            # else:
            bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.3)

        for new_area in context.screen.areas:
            if new_area not in areas:
                break
        else:
            print("fuck")

        opened_area = new_area
        new_area.type = "FILE_BROWSER"
        new_area.ui_type = "ASSETS"

        def change_active_library():
            new_area.spaces.active.params.asset_library_ref = "Assets"

        # the context needs to be updated first, so wait until that's done
        bpy.app.timers.register(change_active_library, first_interval=.001)
        # print(dir(new_area.spaces[0].params))
        # new_area.spaces[0].params.asset_library_ref = "Assets"
        new_area.spaces

        return {"FINISHED"}


addon_keymaps = []


def register():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Window")
    # insert keymap items here
    addon_keymaps.append(km)
    # kmi = km.keymap_items.new(
    #     idname=STRIKE_OT_toggle_asset_browser.bl_idname,
    #     type="SPACE",
    #     value="PRESS",
    #     shift=True,
    #     ctrl=True,
    #     alt=False,
    #     oskey=False,
    # )
    # print(kmi)


def unregister():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
