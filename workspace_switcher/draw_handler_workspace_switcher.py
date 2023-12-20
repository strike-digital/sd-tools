import bpy

from ..handlers import Timer
from .prop_workspace_switcher import get_wswitcher_settings

"""
Monitor for changes in the current workspace.
Unfortunately I don't think there's a better way to do this than just checking
every half a second.
"""

workspace_name: str = ""


def workspace_switch_timer():
    global workspace_name
    workspace = bpy.context.workspace
    if workspace.name != workspace_name:
        workspace_name = workspace.name
        get_wswitcher_settings().set_access_time(workspace)
    return 0.5


Timer(workspace_switch_timer)
