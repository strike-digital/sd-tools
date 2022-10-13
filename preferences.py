from bpy.types import AddonPreferences, UILayout


class TestAddonPreferences(AddonPreferences):
    bl_idname = __package__
    layout: UILayout

    # def draw(self, context):
    #     layout = self.layout