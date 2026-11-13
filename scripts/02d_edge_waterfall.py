"""Phase 2D: replace a bent edge waterfall with a gravity-led cascade.
Blender 5.2+. Reads the current Main scene, backs up the file, then saves in place.
Does not touch the river, upper waterfall, terrain, trees, clouds or campsite.
"""
import bpy
import json
import math
import os
import shutil
from mathutils import Vector

MAIN = "WhisperingPines_Main.blend"
SOURCE = "WATER_EdgeSpill"
COLLECTION = "WP2D_Edge_Waterfall"
OUTPUT = "WP2D_Gravity_Fall"
FOAM = "WP2D_Edge_Foam"
BACKUP = "WhisperingPines_Before_Phase2D.blend"


def make_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def get_material(preferred, backup, fallback_rgba):
    material = bpy.data.materials.get(preferred) or bpy.data.materials.get(backup)
    if material is not None:
        return material
    material = bpy.data.materials.new(preferred)
    material.diffuse_color = fallback_rgba
    return material


def build_strip(name, vertices, faces, material, coll):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    coll.objects.link(ob)
    mesh.materials.append(material)
    return ob


def main():
    source_path = os.path.abspath(bpy.data.filepath)
    if os.path.basename(source_path) != MAIN or os.path.basename(os.path.dirname(source_path)).lower() != "blender":
        raise RuntimeError("Run against blender/" + MAIN + ".")
    if bpy.data.objects.get(OUTPUT) or bpy.data.collections.get(COLLECTION):
        raise RuntimeError("Phase 2D is already present. Restore its backup to rerun cleanly.")
    spill = bpy.data.objects.get(SOURCE)
    if spill is None or spill.type != "MESH":
        raise RuntimeError("WATER_EdgeSpill missing. Do not guess where the waterfall should begin.")
    if len(spill.data.vertices) < 4:
        raise RuntimeError("WATER_EdgeSpill has too few vertices.")
    world = [spill.matrix_world @ v.co for v in spill.data.vertices]
    top_z = max(v.z for v in world)
    # Limit lip candidates to the mesh's actual uppermost water-edge ring.
    lips = [v for v in world if v.z >= top_z - .10]
    if len(lips) < 2:
        raise RuntimeError("Could not identify at least two vertices on the waterfall lip.")
    pairs = [(a, b) for i, a in enumerate(lips) for b in lips[i+1:]]
    left, right = max(pairs, key=lambda pair: (pair[0].xy - pair[1].xy).length_squared)
    width = (right.xy - left.xy).length
    if width < .35 or width > 5.:
        raise RuntimeError("Detected lip width outside safe range: %.3f. Manual inspection required." % width)

    river = bpy.data.objects.get("WATER_Stream")
    if river is None or river.type != "MESH":
        raise RuntimeError("Original WATER_Stream unavailable; cannot verify outlet contact.")
    river_world = [river.matrix_world @ v.co for v in river.data.vertices]
    midpoint = (left + right) * .5
    near = min((v-midpoint).length for v in river_world)
    if near > 3.0:
        raise RuntimeError("Edge spill is too far from river (%.2f units). Refusing disconnected waterfall." % near)

    depth = max(5.0, min(9.0, top_z - min(v.z for v in world)))
    # In world XY the falling water must stay under the lip. Tiny drift < 0.2 Blender units.
    side = right-left
    tangent = Vector((side.x,side.y,0)).normalized()
    forward = Vector((-tangent.y,tangent.x,0))
    if (midpoint - Vector((0,0,midpoint.z))).dot(forward) < 0:
        forward = -forward
    segments = 28
    verts = []
    for i in range(segments+1):
        t = i / segments
        sag = t*t
        drift = forward * (.13*sag)
        wobble = tangent * (.026*math.sin(t*math.pi*3)*math.sin(t*math.pi))
        z = top_z - depth*t
        taper = 1.0 - .13*t
        half = (right-left)*(.5*taper)
        center = midpoint + drift + wobble
        center.z = z
        verts.extend([tuple(center-half), tuple(center+half)])
    faces = [(2*i,2*i+1,2*i+3,2*i+2) for i in range(segments)]
    coll = make_collection(COLLECTION)
    mat = get_material("MAT_waterfall_a", "MAT_water", (.16,.69,.88,1))
    fall = build_strip(OUTPUT, verts, faces, mat, coll)

    # Narrow white froth at the lip, not a separate giant vertical ribbon.
    foam_mat = get_material("MAT_foam", "MAT_waterfall_b", (.85,.96,1.0,1))
    foam_verts = []
    for j in range(3):
        t = j/2
        mid = midpoint + forward * (.01 + .055*t)
        mid.z = top_z - .20*t + .025
        half=(right-left)*(.51-.02*t)
        foam_verts.extend([tuple(mid-half),tuple(mid+half)])
    foam_faces=[(0,1,3,2),(2,3,5,4)]
    build_strip(FOAM,foam_verts,foam_faces,foam_mat,coll)

    # Hide original deformed edge water without deleting it.
    spill.hide_set(True)
    spill.hide_render = True
    spill["WP2D_ArchivedBentFall"] = True

    backups = os.path.join(os.path.dirname(source_path), "checkpoints")
    os.makedirs(backups, exist_ok=True)
    backup = os.path.join(backups, BACKUP)
    if os.path.exists(backup):
        raise RuntimeError("Backup already exists; refusing to overwrite working scene without new rollback point: "+backup)
    shutil.copy2(source_path, backup)

    report = {
        "source": source_path, "backup": backup, "output": source_path,
        "waterfall": OUTPUT, "upper_lip": [list(left),list(right)],
        "top_z": top_z, "width": width, "depth": depth,
        "nearest_original_river_vertex_distance": near,
        "other_water_objects_modified": False,
        "review": [
            "Inspect whether the new cascade lip actually attaches to the river outlet.",
            "The new cascade is primarily vertical, not a physics fluid simulation.",
            "The original waterfall at the upper cliff remains unchanged."
        ]
    }
    with open(os.path.join(os.path.dirname(source_path), "WhisperingPines_Phase2D_Report.json"),"w",encoding="utf8") as file:
        json.dump(report,file,indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=source_path,compress=True)
    print("PHASE 2D SAVED:",source_path)
    print("LIP WIDTH:",round(width,3),"DEPTH:",round(depth,3),"RIVER DISTANCE:",round(near,3))
    print("ROLLBACK:",backup)


if __name__ == "__main__":
    main()
