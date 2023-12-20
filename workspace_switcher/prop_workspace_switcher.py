import time

import bpy
from bpy.types import WorkSpace

from ..btypes import BPropertyGroup


@BPropertyGroup(bpy.types.WindowManager, "workspace_switcher")
class WorkspaceSettings(BPropertyGroup.type):
    def ensure_access_times(self):
        """Ensure all access times exist and are in sync with the current workspaces"""
        times = dict(self.get("_access_times", {}))
        for workspace in bpy.data.workspaces:
            if workspace.name not in times:
                times[workspace.name] = 0
        self["_access_times"] = times

    def get_access_times(self):
        self.ensure_access_times()
        return dict(self["_access_times"])

    def set_access_time(self, workspace: WorkSpace):
        """Set the access time for a specific workspace to the current time"""
        self.ensure_access_times()
        self["_access_times"][workspace.name] = time.time()

    access_times = property(get_access_times)

    @property
    def ordered_workspace_list(self):
        times = self.get_access_times()
        names = list(times.keys())
        names.sort(key=lambda name: times[name], reverse=True)
        workspaces = [bpy.data.workspaces[n] for n in names]
        return workspaces


def get_wswitcher_settings() -> WorkspaceSettings:
    return bpy.context.window_manager.workspace_switcher
