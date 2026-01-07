import json

from ...btypes import BOperator
from ...constants import Files


# TODO: Finish this
@BOperator()
class SD_OT_open_recent_file(BOperator.type):

    def execute(self, context):
        if Files.RECENT_FILE_LIST.exists():
            with open(Files.RECENT_FILE_LIST, "r") as f:
                data = json.load(f)
        else:
            data = {}


def update_file_list(*args):
    print("load")


# Handler(update_file_list, HandlerType.LOAD_POST, persistent=True)
