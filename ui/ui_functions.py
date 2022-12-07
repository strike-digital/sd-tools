import bpy
import blf
from bpy.types import UILayout, Context

"""For useful functions related to UI"""


def dpifac() -> float:
    """Taken from Node Wrangler. Not sure exacly why it works, but it is needed to get the visual position of nodes"""
    prefs = bpy.context.preferences.system
    return prefs.dpi * prefs.pixel_size / 72  # Why 72?


def multi_line_operator(
        layout: UILayout,
        operator: str,
        lines: list[str],
        line_spacing: float = .85,
        padding: float = .4,
        icon: str = "NONE",
):
    """Draw an operator with a multi line label"""
    # Draw the text over multiple rows in a column
    col = layout.column(align=True)
    col.scale_y = line_spacing
    for line in lines:
        row = col.row()
        row.alignment = "CENTER"
        row.label(text=line)

    # The scale needed to cover all the text with the button
    scale = len(lines) * col.scale_y + padding
    col = layout.column(align=True)

    # This is the magic: drawing a property with a negative y scale will push everything drawn below it up.
    # It's very hacky, but it works...
    # I would only advise against using it because it might be broken in future updates.
    propcol = col.column(align=True)
    propcol.scale_y = -scale  # give this column a negative scale
    # This can be any property, it doesn't matter which as it won't be editable.
    propcol.prop(bpy.context.scene.unit_settings, "scale_length")

    # Draw an operator below the prop so that it will be moved up.
    row = col.row(align=True)
    row.scale_y = scale
    row.operator(operator, text=" ", icon=icon)


def wrap_text(self, context: Context, text: str, layout: UILayout, centered: bool = False) -> list[str]:
    """Take a string and draw it over multiple lines so that it is never concatenated."""
    return_text = []
    row_text = ''

    width = context.region.width
    system = context.preferences.system
    ui_scale = system.ui_scale
    width = (4 / (5 * ui_scale)) * width

    dpi = 72 if system.ui_scale >= 1 else system.dpi
    blf.size(0, 11, dpi)

    for word in text.split():
        word = f' {word}'
        line_len, _ = blf.dimensions(0, row_text + word)

        if line_len <= (width - 16):
            row_text += word
        else:
            return_text.append(row_text)
            row_text = word

    if row_text:
        return_text.append(row_text)

    for text in return_text:
        row = layout.row()
        if centered:
            row.alignment = "CENTER"
        row.label(text=text)

    return return_text
