import bpy
from bpy.types import KeyMap
from ...btypes import BOperator


@BOperator("strike")
class STRIKE_OT_toggle_asset_browser(BOperator.type):

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        initial_areas = {a for a in context.screen.areas}
        area = context.area

        opened_area = None
        if area.type == "FILE_BROWSER" and area.ui_type == "ASSETS":
            opened_area = area
        else:
            for a in context.screen.areas:
                if 0 < area.y - (a.y + a.height) < 5 and a.x == area.x:
                    if a.type == "FILE_BROWSER" and a.ui_type == "ASSETS":
                        opened_area = a

        if opened_area:
            with context.temp_override(area=opened_area):
                bpy.ops.screen.area_close()
            opened_area = None
            return self.FINISHED

        with context.temp_override(area=area):
            factor = 300 * context.preferences.view.ui_scale / area.height
            if factor > .5:
                factor = .5
            bpy.ops.screen.area_split(direction='HORIZONTAL', factor=factor)

        for new_area in context.screen.areas:
            if new_area not in initial_areas:
                break
        else:
            print("fuck")

        new_area.type = "FILE_BROWSER"
        new_area.ui_type = "ASSETS"

        def change_active_library():
            # new_area.spaces.active.params.asset_library_ref = "Assets"
            if area.type == "NODE_EDITOR":
                if area.ui_type == "GeometryNodeTree":
                    new_area.spaces.active.params.catalog_id = 'c6ab2da9-d77d-4845-b128-83798299ec6f'
                elif area.ui_type == "ShaderNodeTree":
                    new_area.spaces.active.params.catalog_id = '0d180e60-6043-4efa-996c-cc3ff3a12bc6'
                if area.ui_type == "CompositorNodeTree":
                    new_area.spaces.active.params.catalog_id = '25a32905-0bfd-4443-b902-adec5197e495'
            elif area.type == "VIEW_3D":
                new_area.spaces.active.params.catalog_id = '6fc1d979-f680-4327-9e77-adec8e1adcae'

        # the context needs to be updated first, so wait until that's done
        bpy.app.timers.register(change_active_library, first_interval=.001)
        # print(dir(new_area.spaces[0].params))
        # new_area.spaces[0].params.asset_library_ref = "Assets"
        # new_area.spaces


addon_keymaps: list[KeyMap] = []


def register():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Window")
    # insert keymap items here
    addon_keymaps.append(km)
    kmi = km.keymap_items.new(
        idname=STRIKE_OT_toggle_asset_browser.bl_idname,
        type="SPACE",
        value="PRESS",
        shift=True,
        ctrl=True,
        alt=False,
        oskey=False,
    )
    # print(kmi)


def unregister():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()