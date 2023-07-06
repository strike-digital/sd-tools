from bpy.types import Context
from ...btypes import BOperator


@BOperator("strike")
class STRIKE_OT_set_eevee_transparency(BOperator.type):

    def execute(self, context: Context):
        print("hahah johnathan you have no return value")