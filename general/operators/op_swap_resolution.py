from bpy.types import Context, RENDER_PT_format_presets, UILayout

from ...btypes import BOperator


@BOperator("sd")
class SD_OT_swap_resolution(BOperator.type):

    def execute(self, context: Context):
        render = context.scene.render
        x = render.resolution_x
        render.resolution_x = render.resolution_y
        render.resolution_y = x


def draw_button(self, context: Context):
    layout: UILayout = self.layout
    SD_OT_swap_resolution.draw_button(layout, text="Swap resolution", icon="FILE_REFRESH")
    # layout.label(text="hoho", icon="FILE_REFRESH")


def register():
    RENDER_PT_format_presets.prepend(draw_button)


def unregister():
    RENDER_PT_format_presets.remove(draw_button)
