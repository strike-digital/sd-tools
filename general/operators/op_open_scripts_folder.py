import webbrowser
from pathlib import Path

import bpy
from bpy.types import UILayout, USERPREF_PT_navigation_bar

from ...btypes import BOperator


@BOperator()
class SD_OT_open_scripts_folder(BOperator.type):

    def execute(self, context):
        folder = Path(bpy.utils.user_resource("SCRIPTS")).parent
        webbrowser.open(folder)


def draw_prefs_button(self, context):
    layout: UILayout = self.layout
    col = layout.column(align=True)
    col.scale_y = 1.25
    SD_OT_open_scripts_folder.draw_button(col)


def register():
    USERPREF_PT_navigation_bar.append(draw_prefs_button)


def unregister():
    USERPREF_PT_navigation_bar.remove(draw_prefs_button)
