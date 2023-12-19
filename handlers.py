from __future__ import annotations

from enum import Enum
from typing import Callable

import bpy


class HandlerType(Enum):
    ANIMATION_PLAYBACK_POST = "animation_playback_post"
    ANIMATION_PLAYBACK_PRE = "animation_playback_pre"
    ANNOTATION_POST = "annotation_post"
    ANNOTATION_PRE = "annotation_pre"
    COMPOSITE_CANCEL = "composite_cancel"
    COMPOSITE_POST = "composite_post"
    COMPOSITE_PRE = "composite_pre"
    DEPSGRAPH_UPDATE_POST = "depsgraph_update_post"
    DEPSGRAPH_UPDATE_PRE = "depsgraph_update_pre"
    FRAME_CHANGE_POST = "frame_change_post"
    FRAME_CHANGE_PRE = "frame_change_pre"
    LOAD_FACTORY_PREFERENCES_POST = "load_factory_preferences_post"
    LOAD_FACTORY_STARTUP_POST = "load_factory_startup_post"
    LOAD_POST = "load_post"
    LOAD_POST_FAIL = "load_post_fail"
    LOAD_PRE = "load_pre"
    OBJECT_BAKE_CANCEL = "object_bake_cancel"
    OBJECT_BAKE_COMPLETE = "object_bake_complete"
    OBJECT_BAKE_PRE = "object_bake_pre"
    REDO_POST = "redo_post"
    REDO_PRE = "redo_pre"
    RENDER_CANCEL = "render_cancel"
    RENDER_COMPLETE = "render_complete"
    RENDER_INIT = "render_init"
    RENDER_POST = "render_post"
    RENDER_PRE = "render_pre"
    RENDER_STATS = "render_stats"
    RENDER_WRITE = "render_write"
    SAVE_POST = "save_post"
    SAVE_POST_FAIL = "save_post_fail"
    SAVE_PRE = "save_pre"
    UNDO_POST = "undo_post"
    UNDO_PRE = "undo_pre"
    VERSION_UPDATE = "version_update"
    XR_SESSION_START_PRE = "xr_session_start_pre"
    PERSISTENT = "persistent"


handlers: list[Handler] = []


class Handler:
    """
    Instantiate to create a new handler according the given arguments.

    This is safer than using the built in functions, as if a handler is not removed when the addon is unregistered,
    it will persist until Blender is closed.
    This is not a problem when using this class as all draw handlers created by it are removed automatically.
    """

    def __init__(self, callback: Callable, handler_type: HandlerType, persistent=False):
        if persistent:
            callback = bpy.app.handlers.persistent(callback)
        self.callback = callback
        self.handler_type = handler_type

        handler_list: list = getattr(bpy.app.handlers, handler_type.value)
        handler_list.append(callback)

        global handlers
        handlers.append(self)

    def remove(self):
        handler_list: list = getattr(bpy.app.handlers, self.handler_type.value)
        handler_list.remove(self.callback)

        global handlers
        handlers.remove(self)


class DrawType(Enum):
    POST_PIXEL = "POST_PIXEL"
    PRE_VIEW = "PRE_VIEW"
    POST_VIEW = "POST_VIEW"
    BACKDROP = "BACKDROP"


class RegionType(Enum):
    WINDOW = "WINDOW"
    HEADER = "HEADER"
    CHANNELS = "CHANNELS"
    TEMPORARY = "TEMPORARY"
    UI = "UI"
    TOOLS = "TOOLS"
    TOOL_PROPS = "TOOL_PROPS"
    PREVIEW = "PREVIEW"
    HUD = "HUD"
    NAVIGATION_BAR = "NAVIGATION_BAR"
    EXECUTE = "EXECUTE"
    FOOTER = "FOOTER"
    TOOL_HEADER = "TOOL_HEADER"
    XR = "XR"


class DrawHandler:
    """
    Instantiate to create a new draw handler.

    This is safer than using the built in functions, as if a draw handler is not removed when the addon is unregistered,
    it will persist until Blender is closed.
    This is not a problem when using this class as all draw handlers created by it are removed automatically.
    """

    def __init__(
        self,
        func: Callable,
        space: bpy.types.Space,
        region_type: RegionType = RegionType.WINDOW,
        draw_type: DrawType = DrawType.POST_PIXEL,
        args: tuple = (),
    ):
        self.handler = space.draw_handler_add(
            func,
            args,
            region_type.value,
            draw_type.value,
        )
        self.space = space
        self.region_type = region_type

        global draw_handlers
        draw_handlers.append(self)

    def remove(self):
        self.space.draw_handler_remove(self.handler, self.region_type.value)

        global draw_handlers
        draw_handlers.remove(self)


draw_handlers: list[DrawHandler] = []


timers: list[Timer] = []


class Timer:
    def run(self):
        if not self.finished:
            return self.func()

    def __init__(self, func: Callable, first_interval: float = 0, persistent: bool = False):
        self.finished = False
        self.func = func
        bpy.app.timers.register(self.run, first_interval=first_interval, persistent=persistent)
        global timers
        timers.append(self)

    def remove(self):
        self.finished = True

        global timers
        timers.remove(self)


def unregister():
    """Clean up unremoved handlers"""
    global handlers
    for handler in handlers:
        handler.remove()

    global draw_handlers
    for handler in draw_handlers:
        handler.remove()

    global timers
    for timer in timers:
        timer.remove()
