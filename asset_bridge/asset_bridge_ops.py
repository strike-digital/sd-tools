import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from mathutils import Vector
from ..btypes import BOperator


@BOperator("strike")
class STRIKE_OT_dummy_import(Operator):

    asset_id: StringProperty()

    collection_name: StringProperty()

    def invoke(self, context, event):
        self.mouse_pos_region = Vector((event.mouse_region_x, event.mouse_region_y))
        self.mouse_pos_window = Vector((event.mouse_x, event.mouse_y))
        return self.execute(context)

    def execute(self, context):
        if self.collection_name:
            collection = bpy.data.collections[self.collection_name]
        else:
            collection = context.collection
        collection_name = collection.name
        location = Vector()
        for obj in collection.objects:
            location += obj.location
        location /= len(collection.objects)

        task = context.window_manager.asset_bridge.new_task()
        task.new_progress(100)
        asset_id = "_".join(collection.name.split("_")[:-1])
        asset_id = self.asset_id or asset_id
        bpy.ops.asset_bridge.draw_import_progress(
            "INVOKE_DEFAULT",
            task_name=task.name,
            location=location,
            asset_id=asset_id,
        )
        task_name = task.name

        def traverse_tree(t):
            yield t
            for child in t.children:
                yield from traverse_tree(child)

        def update_progress():
            task = context.window_manager.asset_bridge.tasks[task_name]

            if task.progress.progress >= 100:
                layer_collections = {l.collection.name: l for l in traverse_tree(context.view_layer.layer_collection)}
                layer_collection = layer_collections[collection_name]
                # collection = bpy.data.collections[collection_name]
                # collection.hide_viewport = False
                layer_collection.hide_viewport = False
                task.finish()
                for area in context.screen.areas:
                    area.tag_redraw()
                print("Finish", collection, collection.hide_viewport)
                return

            task.update_progress(task.progress.progress + 1)
            print("ho")
            return .02

        bpy.app.timers.register(update_progress, first_interval=.02)
        return {"FINISHED"}