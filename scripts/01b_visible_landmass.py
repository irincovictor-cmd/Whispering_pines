"""Whispering Pines — Phase 1B visible landmass reconstruction.
Run against pristine source; produces a stable working filename.
Does NOT modify clouds, water, vegetation, camp, camera or lighting.
"""
import bpy
import json
import math
import os
import random
import shutil
from mathutils import Vector

SOURCE = "WhisperingPines_Blockout_v01.blend"
MAIN = "WhisperingPines_Main.blend"
TERRAIN = ("TERRAIN_Island_Top", "TERRAIN_Island_Underside")
COLLECTION = "WP_Phase1B_Underside"
SEED = 1306


def smooth(value):
    t = max(0.0, min(1.0, value))
    return t*t*(3.0 - 2.0*t)


def make_spire(name, x, y, upper_z, length, radius, material, collection, rng):
    # Closed, slightly asymmetric tapered cliff shard; top ring embeds in underside.
    sides = 7
    angles = [2*math.pi*i/sides for i in range(sides)]
    levels = [(upper_z, radius), (upper_z-length*.33, radius*.82),
              (upper_z-length*.72, radius*.42)]
    vertices = []
    for level, (z, width) in enumerate(levels):
        for i, angle in enumerate(angles):
            offset = 1 + .13*math.sin(i*2.7 + level*1.3 + x)
            vertices.append((x+math.cos(angle)*width*offset,
                             y+math.sin(angle)*width*offset,
                             z + .05*math.sin(i*1.71+level)))
    tip = len(vertices)
    vertices.append((x+radius*rng.uniform(-.22,.22),
                     y+radius*rng.uniform(-.22,.22), upper_z-length))
    faces = []
    for layer in range(len(levels)-1):
        for i in range(sides):
            j=(i+1)%sides
            a=layer*sides+i; b=layer*sides+j
            c=(layer+1)*sides+j; d=(layer+1)*sides+i
            faces.append((a,b,c,d))
    for i in range(sides):
        faces.append(((len(levels)-1)*sides+i,
                      (len(levels)-1)*sides+(i+1)%sides, tip))
    faces.append(tuple(reversed(tuple(range(sides)))))
    mesh=bpy.data.meshes.new(name+"_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    collection.objects.link(ob)
    if material:
        ob.data.materials.append(material)
    return ob


def main():
    filepath=os.path.abspath(bpy.data.filepath)
    if (os.path.basename(filepath)!=SOURCE or
            os.path.basename(os.path.dirname(filepath)).lower()!="source"):
        raise RuntimeError("Open source/"+SOURCE+" — the original scene — before running Phase 1B.")
    root=os.path.dirname(os.path.dirname(filepath))
    outdir=os.path.join(root,"blender")
    os.makedirs(outdir,exist_ok=True)
    destination=os.path.join(outdir,MAIN)
    top,bottom=(bpy.data.objects.get(name) for name in TERRAIN)
    if not top or not bottom or top.type!="MESH" or bottom.type!="MESH":
        raise RuntimeError("Expected top and underside terrain meshes were not found.")
    if min(len(top.data.vertices),len(bottom.data.vertices))<12:
        raise RuntimeError("Terrain does not contain enough vertices for a safe expansion.")

    verts=[top.matrix_world @ v.co for v in top.data.vertices]
    min_x,max_x=min(v.x for v in verts),max(v.x for v in verts)
    min_y,max_y=min(v.y for v in verts),max(v.y for v in verts)
    center=Vector(((min_x+max_x)/2,(min_y+max_y)/2,0))
    waterfall=bpy.data.objects.get("CLIFF_Waterfall_Rock")
    camp=bpy.data.objects.get("CAMP_Campfire")
    forward=(camp.matrix_world.translation-waterfall.matrix_world.translation) if waterfall and camp else Vector((0,-1,0))
    forward.z=0
    if forward.length<.001:
        forward=Vector((0,-1,0))
    forward.normalize()
    lateral=Vector((-forward.y,forward.x,0))
    uv=[((v-center).dot(lateral),(v-center).dot(forward)) for v in verts]
    side_reach=max(max(abs(u) for u,v in uv),.01)
    front_reach=max(max(v for u,v in uv),.01)
    back_reach=max(max(-v for u,v in uv),.01)
    rng=random.Random(SEED)
    report={"input":filepath,"working_file":destination,"clouds_removed":0,
            "untouched_objects":"All except terrain top/underside",
            "expanded_terrain":list(TERRAIN),
            "created_underside_objects":[],"deleted_objects":[],
            "notes":["Cloud shapes are intentionally preserved.",
                     "River and waterfall are still original and require the next water pass.",
                     "No unidentified sub-island was deleted; inspect in Blender."]}

    def expand(p):
        delta=p-center
        u,v=delta.dot(lateral),delta.dot(forward)
        outward=smooth((abs(u)/side_reach-.30)/.70)
        reach=front_reach if v>=0 else back_reach
        axial=smooth((abs(v)/reach-.30)/.70)
        # More visible than Phase 1A; interior remains anchored.
        u*=1+.48*outward
        v*=1+(.35 if v>=0 else .04)*axial
        return Vector((center.x+lateral.x*u+forward.x*v,
                       center.y+lateral.y*u+forward.y*v,p.z))

    z=[(bottom.matrix_world @ v.co).z for v in bottom.data.vertices]
    zmin,zmax=min(z),max(z)
    depth=max(zmax-zmin,.1)
    for obj in (top,bottom):
        if obj.data.users>1:
            obj.data=obj.data.copy()
        inverse=obj.matrix_world.inverted_safe()
        positions=[]
        for vert in obj.data.vertices:
            old=obj.matrix_world @ vert.co
            new=expand(old)
            if obj is bottom:
                # Preserve upper seam; only deeper rocks get irregular relief.
                amount=smooth((zmax-old.z)/depth)
                ripple=math.sin(old.x*1.19+old.y*.58)*math.cos(old.y*1.36-old.x*.41)
                new.z-=depth*(.115+.065*ripple)*amount
            positions.append(inverse @ new)
        for vert,new in zip(obj.data.vertices,positions):
            vert.co=new
        obj.data.update()
        obj["WP_terrain_phase"]="1B"

    group=bpy.data.collections.get(COLLECTION)
    if not group:
        group=bpy.data.collections.new(COLLECTION)
        bpy.context.scene.collection.children.link(group)
    for obj in list(group.objects):
        bpy.data.objects.remove(obj,do_unlink=True)

    # Extra silhouette detail: lower rock shards with their upper rings
    # embedded into the central lower underside (not free-floating crystals).
    # These are *secondary* additions and do not replace the existing underside.
    material=bottom.data.materials[0] if bottom.data.materials else None
    beneath=[bottom.matrix_world @ v.co for v in bottom.data.vertices]
    bottom_mid=(min(p.z for p in beneath)+max(p.z for p in beneath))*.5
    for i in range(13):
        angle=2*math.pi*(i/13)+rng.uniform(-.2,.2)
        radius_factor=rng.uniform(.12,.49)
        origin=center+lateral*(side_reach*radius_factor*math.cos(angle))+forward*(front_reach*radius_factor*math.sin(angle))
        length=depth*rng.uniform(.32,.72)
        width=min(side_reach,front_reach)*rng.uniform(.08,.14)
        ob=make_spire("WP1B_Hanging_Rock_%02d"%(i+1),
                      origin.x,origin.y,bottom_mid+depth*.11,
                      length,width,material,group,rng)
        report["created_underside_objects"].append(ob.name)

    # Keep single permanent output filename; preserve previous working version locally.
    if os.path.exists(destination):
        checkpoint=os.path.join(outdir,"checkpoints")
        os.makedirs(checkpoint,exist_ok=True)
        backup=os.path.join(checkpoint,"WhisperingPines_Before_Phase1B.blend")
        if not os.path.exists(backup):
            shutil.copy2(destination,backup)
            report["previous_file_backup"]=backup
        else:
            report["notes"].append("Existing pre-1B backup retained; no new backup created.")
    bpy.ops.wm.save_as_mainfile(filepath=destination,compress=True)
    report_file=os.path.join(outdir,"WhisperingPines_Phase1B_report.json")
    with open(report_file,"w",encoding="utf8") as f:
        json.dump(report,f,indent=2)
    print("PHASE 1B SAVED:",destination)
    print("HANGING ROCKS CREATED:",len(report["created_underside_objects"]))
    print("OTHER OBJECTS MOVED: 0")
    print("CLOUDS PRESERVED: YES")
    print("REMINDER: VISUAL REVIEW REQUIRED")


if __name__=="__main__":
    main()
