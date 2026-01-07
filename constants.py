
from pathlib import Path

import bpy


class Dirs:
    ADDON_DIR = Path(__file__).parent
    CONFIG_DIR = Path(bpy.utils.user_resource("CONFIG"))
    CACHE_DIR = Path(bpy.utils.script_path_user()).parents[2] / "data" / "sd_tools"


class Files:
    BL_RECENT_FILES = Dirs.CONFIG_DIR / "recent-files.txt"
    RECENT_FILE_LIST = Dirs.CACHE_DIR / "recent_files.json"
