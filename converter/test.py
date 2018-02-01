import bpy
import bmesh
from mathutils import Vector
import math

ROAD_HEIGHT_CAR_MM = 0.82 # 3 x 0.25-0.3mm layers
ROAD_HEIGHT_PEDESTRIAN_MM = 1.5
BUILDING_HEIGHT_MM = 2.9
BASE_HEIGHT_MM = 10
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
    # bpy.ops.object.select_all(action='SELECT') # it's handy to have everything selected initially
    bpy.ops.wm.save_as_mainfile(filepath=blend_path, check_existing=False, compress=True)

def depress_buildings(base):
    z_max_base = max(v.co[2] for v in base.data.vertices)
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    buildings = [o for o in bpy.context.scene.objects if o.name.startswith('Building')]
    for building in buildings:
        # remove faces
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        print(building)
        building.select = True
        bpy.context.scene.objects.active = building
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.dissolve_limited()
        bpy.ops.mesh.delete(type='ONLY_FACE')
        building.select = False
        print("removed.")

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # identify base vertices
        def is_base_vertex(z_min, vertex):
            return abs(vertex.co[2] - z_min) < 0.1

        vertices = building.data.vertices
        z_min = min(v.co[2] for v in vertices)
        base_vertices = [v for v in vertices if is_base_vertex(z_min, v)]
        other_vertices = [v for v in vertices if not is_base_vertex(z_min, v)]

        # remove all other vertices
        sel_mode = bpy.context.tool_settings.mesh_select_mode
        bpy.context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        for v in other_vertices:
            v.select = True
            
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.delete(type='VERT')

        building.location += Vector((0, 0, 5))

        print('extruding')

        # extrude building down
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = building
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={ "value": (0.0, 0.0, -30) })

        bpy.context.tool_settings.mesh_select_mode = sel_mode

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # # cut vertices into base
        # bpy.context.scene.objects.active = base
        # base.select = True
        # bpy.ops.object.mode_set(mode = 'EDIT')
        # bm = bmesh.from_edit_mesh(base.data)
        # for v in base_vertices:
        #     print("new VERTEX")
        #     bm.verts.new((v.co[0], v.co[1], z_max_base))
        # bmesh.update_edit_mesh(base.data)

        # # join building to base
        # bpy.ops.object.mode_set(mode = 'OBJECT')
        # bpy.ops.object.select_all(action='DESELECT')
        # bpy.context.scene.objects.active = base
        # base.select = True
        # building.select = True
        # bpy.ops.object.join()

        # bpy.ops.object.mode_set(mode = 'EDIT')
        # bpy.ops.mesh.intersect()       
        # building.select = False
        # base.select = False 
        # bpy.context.scene.objects.active = base

scale = 1000
obj_path = "map2.obj"
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

depress_buildings(base_cube)
export_blend_file("map_out.blend")
