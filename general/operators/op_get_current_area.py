from bpy.types import Area
from mathutils import Vector as V

from ...btypes import BOperator, ExecContext

current_area = None


@BOperator()
class SD_OT_get_current_area(BOperator.type):
    """Get the area currently under the cursor"""

    def invoke(self, context, event):
        global current_area
        for area in context.screen.areas:
            area_min = V((area.x, area.y))
            area_max = V((area.x + area.width, area.y + area.height))
            if (self.mouse_window.x > area_min.x and self.mouse_window.y > area_min.y) and (
                self.mouse_window.x < area_max.x and self.mouse_window.y < area_max.y
            ):
                current_area = area
                return self.FINISHED
        current_area = None
        return self.FINISHED


def get_current_area() -> Area | None:
    SD_OT_get_current_area.run(ExecContext.INVOKE)
    global current_area
    return current_area
