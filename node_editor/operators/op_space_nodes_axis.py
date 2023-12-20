# from statistics import mean
# from bpy.props import BoolProperty
# from mathutils import Vector
# from ...btypes import BOperator

# @BOperator("sd")
# class SD_OT_space_nodes_axis(BOperator.type):

#     x: BoolProperty(default=True)

#     @classmethod
#     def poll(cls, context):
#         if not context.space_data or context.area.type != "NODE_EDITOR":
#             return False
#         return True

#     def execute(self, context):
#         nodes = context.selected_nodes
#         mean_location = Vector((mean(n.location.x for n in nodes), mean(n.location.y for n in nodes)))
#         for node in nodes:
#             if self.x:
#                 mean_y = round(mean_location.y / 20) * 20
#                 node.location.y = mean_y
#             else:
#                 mean_x = round(mean_location.x / 20) * 20
#                 node.location.x = mean_x
