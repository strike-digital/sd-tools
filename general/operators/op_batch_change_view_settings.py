import bpy
from bpy.props import FloatProperty
from bpy.types import Context
from ...btypes import BOperator


@BOperator("strike", undo=True)
class STRIKE_OT_batch_change_view_settings(BOperator.type):
    """Change view settings in all screens and viewports in the file"""

    focal_length: FloatProperty(name="Focal Length", subtype="DISTANCE_CAMERA")
    clip_start: FloatProperty(name="Clip Start", subtype="DISTANCE", default=.01)
    clip_end: FloatProperty(name="Clip End", subtype="DISTANCE", default=1000)

    def invoke(self, context: Context, event):
        if context.area.type == "VIEW_3D":
            space = context.area.spaces.active
            self.focal_length = space.lens
            self.clip_start = space.clip_start
            self.clip_end = space.clip_end
        return self.call_popup_confirm()

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "focal_length")
        layout.prop(self, "clip_start")
        layout.prop(self, "clip_end")

    def execute(self, context):
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type != "VIEW_3D":
                    continue
                space = area.spaces.active
                space.lens = self.focal_length
                space.clip_start = self.clip_start
                space.clip_end = self.clip_end