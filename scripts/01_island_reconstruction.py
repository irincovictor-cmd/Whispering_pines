"""Whispering Pines Phase 1: balanced terrain expansion.
Run on the ORIGINAL baseline file, never the generated checkpoint.
Requires Blender Python (bpy). Saves a separate scene and JSON report.
"""
import bpy
import json
import os
from mathutils import Vector

TOP = "TERRAIN_Island_Top"
UNDER = "TERRAIN_Island_Underside"
SIDE_AMOUNT = 0.30
FRONT_AMOUNT = 0.26
BACK_AMOUNT = 0.035
CORE_FRACTION = 0.37
PROTECTED = ("CAM_", "LIGHT_", "BACKDROP_", "BRIDGE_", "CLIFF_", "CAMP_")
OUTPUT = "WhisperingPines_Phase1_Expanded.blend"


def smooth(t):
    t = max(0., min(1., t))
    return t * t * (3. - 2. * t)


def connected_groups(mesh):
    parent = list(range(len(mesh.vertices)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for e in mesh.edges:
        x, y = (find(i) for i in e.vertices)
        parent[x] = y
    sizes = {}
    for i in range(len(parent)):
        root = find(i)
        sizes[root] = sizes.get(root, 0) + 1
    return sorted(sizes.values(), reverse=True)


def main():
    if not bpy.data.filepath:
        raise RuntimeError("Open the original .blend first.")
    src = os.path.abspath(bpy.data.filepath)
    if os.path.basename(src) != "WhisperingPines_Blockout_v01.blend":
        raise RuntimeError("Only run against WhisperingPines_Blockout_v01.blend.")
    directory = os.path.dirname(src)
    root = os.path.dirname(directory) if os.path.basename(directory).lower() == "source" else directory
    output_dir = os.path.join(root, "blender")
    os.makedirs(output_dir, exist_ok=True)
    dst = os.path.join(output_dir, OUTPUT)
    if os.path.exists(dst):
        raise RuntimeError("Existing checkpoint detected; rename/back it up before rerunning: " + dst)
    terrain = [bpy.data.objects.get(TOP), bpy.data.objects.get(UNDER)]
    if not all(o and o.type == "MESH" for o in terrain):
        raise RuntimeError("Expected top/underside terrain meshes not found.")
    if any(len(o.data.vertices) < 12 for o in terrain):
        raise RuntimeError("Terrain geometry incomplete.")
    top, under = terrain
    world = [top.matrix_world @ v.co for v in top.data.vertices]
    xmin, xmax = min(p.x for p in world), max(p.x for p in world)
    ymin, ymax = min(p.y for p in world), max(p.y for p in world)
    origin = Vector(((xmin+xmax)*.5, (ymin+ymax)*.5, 0))
    waterfall = bpy.data.objects.get("CLIFF_Waterfall_Rock")
    campfire = bpy.data.objects.get("CAMP_Campfire")
    direction = ((campfire.matrix_world.translation - waterfall.matrix_world.translation)
                 if waterfall and campfire else Vector((0,-1,0)))
    direction.z = 0
    if direction.length < .001:
        direction = Vector((0,-1,0))
    forward = direction.normalized()
    side = Vector((-forward.y, forward.x, 0))
    uv = [((p-origin).dot(side), (p-origin).dot(forward)) for p in world]
    max_u = max(max(abs(u) for u,v in uv), .01)
    max_front = max(max(v for u,v in uv), .01)
    max_back = max(max(-v for u,v in uv), .01)

    def deform(point):
        delta = point - origin
        u, v = delta.dot(side), delta.dot(forward)
        edge_u = smooth((abs(u)/max_u - CORE_FRACTION) / (1-CORE_FRACTION))
        edge_v = smooth((abs(v)/(max_front if v>=0 else max_back)-CORE_FRACTION)/(1-CORE_FRACTION))
        nu = u * (1 + SIDE_AMOUNT*edge_u)
        nv = v * (1 + (FRONT_AMOUNT if v>=0 else BACK_AMOUNT)*edge_v)
        return Vector((origin.x + nu*side.x + nv*forward.x,
                       origin.y + nu*side.y + nv*forward.y, point.z))

    report = {
        "source": src, "output": dst, "scene_object_count": len(bpy.data.objects),
        "terrain_component_sizes": {o.name: connected_groups(o.data) for o in terrain},
        "side_expansion": SIDE_AMOUNT, "front_expansion": FRONT_AMOUNT,
        "rear_expansion": BACK_AMOUNT, "front_direction": list(forward)[:2],
        "removed_sub_island_objects": [], "moved_decorations": [],
        "warnings": []
    }
    if any(len(report["terrain_component_sizes"][o.name])>1 for o in terrain):
        report["warnings"].append("Detached mesh components found: review before deleting a sub-island.")
    # Delete only clearly labeled subsidiary island objects; never infer from proximity or color.
    for obj in list(bpy.data.objects):
        n = obj.name.lower().replace("-", "_").replace(" ", "_")
        if "sub_island" in n or "secondary_island" in n or bool(obj.get("whispering_pines_sub_island", False)):
            if obj in terrain:
                raise RuntimeError("Terrain cannot be safely marked as a sub-island.")
            report["removed_sub_island_objects"].append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    if not report["removed_sub_island_objects"]:
        report["warnings"].append("No explicitly identified sub-island: left unidentified meshes intact.")

    for obj in terrain:
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        inverse = obj.matrix_world.inverted_safe()
        transformed = [inverse @ deform(obj.matrix_world @ v.co) for v in obj.data.vertices]
        for v, coordinate in zip(obj.data.vertices, transformed):
            v.co = coordinate
        obj.data.update()
        obj["WP_Phase1_Expanded"] = True

    for obj in bpy.data.objects:
        if obj in terrain or obj.type not in {"MESH","CURVE","FONT","EMPTY"}:
            continue
        if obj.name.startswith(PROTECTED) or obj.name == "RiverFlowOrigin":
            continue
        previous = obj.matrix_world.translation.copy()
        updated = deform(previous)
        if (updated-previous).length > .0005:
            matrix = obj.matrix_world.copy()
            matrix.translation = updated
            obj.matrix_world = matrix
            report["moved_decorations"].append(obj.name)

    col = bpy.data.collections.get("PHASE1_Island_Reconstruction")
    if not col:
        col = bpy.data.collections.new("PHASE1_Island_Reconstruction")
        bpy.context.scene.collection.children.link(col)
    bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True)
    with open(os.path.join(output_dir, "WhisperingPines_Phase1_report.json"), "w", encoding="utf8") as file:
        json.dump(report, file, indent=2)
    print("PHASE 1 CHECKPOINT:", dst)
    print("DECORATIONS MOVED:", len(report["moved_decorations"]))
    for warning in report["warnings"]:
        print("REVIEW:", warning)


if __name__ == "__main__":
    main()
