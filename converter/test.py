import bpy
from mathutils import Vector
import math

ROAD_HEIGHT_CAR_MM = 0.82 # 3 x 0.25-0.3mm layers
ROAD_HEIGHT_PEDESTRIAN_MM = 1.5
BUILDING_HEIGHT_MM = 2.9
BASE_HEIGHT_MM = 0.6
BASE_OVERLAP_MM = 0.01
WATER_AREA_DEPTH_MM = 1.5
WATER_WAVE_DISTANCE_MM = 10.3
WATERWAY_DEPTH_MM = 0.55 # 2 x 0.25-0.3mm layers
BORDER_WIDTH_MM = 1.2 # 3 shells
BORDER_HEIGHT_MM = (ROAD_HEIGHT_PEDESTRIAN_MM + BUILDING_HEIGHT_MM) / 2
BORDER_HORIZONTAL_OVERLAP_MM = 0.05
MARKER_HEIGHT_MM = BUILDING_HEIGHT_MM + 2
MARKER_RADIUS_MM = MARKER_HEIGHT_MM * 0.5

def get_obj_bounds(obj):
    me = obj.data
    if not hasattr(me, 'vertices') or len(me.vertices) == 0:
        print(obj.name)
        return obj.location[0], obj.location[1], obj.location[0], obj.location[1]
    
    verts_sel = [v.co for v in me.vertices]
    # print("vertices: ", verts_sel)
    min_obj_x = min(verts_sel, key=lambda x:x[0])[0]
    min_obj_y = min(verts_sel, key=lambda x:x[1])[1]
    max_obj_x = max(verts_sel, key=lambda x:x[0])[0]
    max_obj_y = max(verts_sel, key=lambda x:x[1])[1]

    return (min_obj_x, min_obj_y, max_obj_x, max_obj_y)

def get_scene_bounds():
    obj_bounds = list(map(get_obj_bounds, bpy.context.scene.objects))
    # for o in obj_bounds:
    #     print(o)
    min_x = min(obj_bounds, key=lambda x:x[0])[0]
    min_y = min(obj_bounds, key=lambda x:x[1])[1]
    max_x = max(obj_bounds, key=lambda x:x[2])[2]
    max_y = max(obj_bounds, key=lambda x:x[3])[3]
    return min_x, min_y, max_x, max_y

def create_cube(min_x, min_y, max_x, max_y, min_z, max_z):
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent()
    bpy.ops.object.mode_set(mode = 'OBJECT')
    cube.location = [ (min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2 ]
    cube.scale = [ (max_x - min_x) / 2, (max_y - min_y) / 2, (max_z - min_z) / 2 ]
    bpy.context.scene.update() # flush changes to location and scale
    return cube


# def get_scene_bounding_box():
#     min_x = math.inf
#     min_y = math.inf
#     max_x = -math.inf
#     max_y = -math.inf
#     obj_bounds = map(get_obj_bounds, bpy.context.scene.objects)
#     for obj in bpy.context.scene.objects:
#         if obj.name != "Building Art Building":
#             continue

#         obj_bounds = get_obj_bounds(obj)
#         # pivot = sum(verts_sel, Vector()) / len(verts_sel)
#         # global_pos = obj.matrix_world * pivot
#         # print('Object: {0}, Dimensions: {1}, min x: {2}, min y: {3}, max x: {4}, max y: {5}'.format(obj.name, obj.dimensions, min_obj_x, min_obj_y, max_obj_x, max_obj_y))
#         # print()
#         # obj.select = False

#         # min_x = min(obj_dimens, key=lambda x:x[0])[0]
#         # min_y = min(obj_dimens, key=lambda x:x[1])[1]
#         # max_x = max(obj_dimens, key=lambda x:x[0])[0]
#         # max_y = max(obj_dimens, key=lambda x:x[1])[1]
#         # min_x = min(min_x, glo)

#     return min_x, min_y, max_x, max_y

def import_obj_file(obj_path):
    bpy.ops.import_scene.obj(filepath=obj_path, axis_forward='X', axis_up='Y')

def export_blend_file(blend_path):
    bpy.ops.object.select_all(action='SELECT') # it's handy to have everything selected initially
    bpy.ops.wm.save_as_mainfile(filepath=blend_path, check_existing=False, compress=True)

scale = 1000
obj_path = "/Users/jackarms/Desktop/touch-mapper/OSM2World/build/map2.obj"
import_obj_file(obj_path)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(rotation=True)
# bpy.context.scene.update()
box = get_scene_bounds()
min_x, min_y, max_x, max_y = box
mm_to_units = scale / 1000
# add_borders(min_x, min_y, max_x, max_y, BORDER_WIDTH_MM * mm_to_units, 0, BORDER_HEIGHT_MM * mm_to_units, (BUILDING_HEIGHT_MM + 1) * mm_to_units)
base_height = BASE_HEIGHT_MM * mm_to_units
overlap = BASE_OVERLAP_MM * mm_to_units # move cube this much up so that it overlaps enough with objects they merge into one object
base_cube = create_cube(min_x, min_y, max_x, max_y, -base_height + overlap, overlap)
base_cube.name = 'Base'
print(box)

export_blend_file("/Users/jackarms/Desktop/touch-mapper/OSM2World/build/map2.blend")
