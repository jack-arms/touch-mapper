import bpy
from mathutils import Vector
import math

def get_obj_bounds(obj):
    me = obj.data
    verts_sel = [v.co for v in me.vertices]
    # print("vertices: ", verts_sel)
    min_obj_x = min(verts_sel, key=lambda x:x[0])[0]
    min_obj_y = min(verts_sel, key=lambda x:x[1])[1]
    max_obj_x = max(verts_sel, key=lambda x:x[0])[0]
    max_obj_y = max(verts_sel, key=lambda x:x[1])[1]

    return (min_obj_x, min_obj_y, max_obj_x, max_obj_y)

def get_scene_bounding_box():
    min_x = math.inf
    min_y = math.inf
    max_x = -math.inf
    max_y = -math.inf
    obj_bounds = map(get_obj_bounds, bpy.context.scene.objects)
    for obj in bpy.context.scene.objects:
        if obj.name != "Building Art Building":
            continue


        # pivot = sum(verts_sel, Vector()) / len(verts_sel)
        # global_pos = obj.matrix_world * pivot
        # print('Object: {0}, Dimensions: {1}, min x: {2}, min y: {3}, max x: {4}, max y: {5}'.format(obj.name, obj.dimensions, min_obj_x, min_obj_y, max_obj_x, max_obj_y))
        # print()
        # obj.select = False

        # min_x = min(obj_dimens, key=lambda x:x[0])[0]
        # min_y = min(obj_dimens, key=lambda x:x[1])[1]
        # max_x = max(obj_dimens, key=lambda x:x[0])[0]
        # max_y = max(obj_dimens, key=lambda x:x[1])[1]
        # min_x = min(min_x, glo)

    return min_x, min_y, max_x, max_y

def import_obj_file(obj_path):
    bpy.ops.import_scene.obj(filepath=obj_path, axis_forward='X', axis_up='Y')

obj_path = "C:/Users/jacka/Documents/projects/touch-mapper/OSM2World/build/map2.obj"
import_obj_file(obj_path)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(rotation=True)
# bpy.context.scene.update()
box = get_scene_bounding_box()
print(box)
