"""Whispering Pines: read-only water/terrain geometry export, Blender 5.x.
Does not save or alter the .blend. Generates a JSON inspection report.
"""
import bpy, os, json, math
from mathutils import Vector

def vec(v):
    return [round(float(x),5) for x in v]

def world_bounds(o):
    p=[o.matrix_world @ Vector(corner) for corner in o.bound_box]
    lo=[min(q[i] for q in p) for i in range(3)]
    hi=[max(q[i] for q in p) for i in range(3)]
    return {"min":vec(lo),"max":vec(hi),"size":vec([hi[i]-lo[i] for i in range(3)])}

def object_entry(o):
    result={"name":o.name,"type":o.type,"collection_names":[c.name for c in o.users_collection],
            "location":vec(o.matrix_world.translation),"rotation":vec(o.rotation_euler),
            "scale":vec(o.scale),"bounds":world_bounds(o),
            "hide_viewport":o.hide_viewport,"hide_render":o.hide_render}
    if o.type=="MESH":
        result["vertices"]=len(o.data.vertices)
        result["faces"]=len(o.data.polygons)
        result["materials"]=[m.name if m else None for m in o.data.materials]
        result["world_vertex_samples"]=[vec(o.matrix_world @ o.data.vertices[i].co)
           for i in range(0,len(o.data.vertices),max(1,len(o.data.vertices)//80))][:81]
    return result

def ray_terrain(o, x, y):
    inv=o.matrix_world.inverted_safe()
    origin=inv @ Vector((x,y,1000))
    direction=(inv.to_3x3() @ Vector((0,0,-1))).normalized()
    ok,p,_,_=o.ray_cast(origin,direction,distance=4000)
    return round(float((o.matrix_world @ p).z),5) if ok else None

def main():
    fp=os.path.abspath(bpy.data.filepath)
    if os.path.basename(fp)!="WhisperingPines_Main.blend":
        raise RuntimeError("Open blender/WhisperingPines_Main.blend first.")
    root=os.path.dirname(os.path.dirname(fp))
    report={"file":fp,"blender_version":bpy.app.version_string,
            "scene":bpy.context.scene.name,
            "frame":bpy.context.scene.frame_current,
            "water_related":[],"terrain_related":[],"bridge_related":[],"landmarks":{},
            "terrain_grid":[],"warnings":[]}
    for o in bpy.data.objects:
        name=o.name.lower()
        if "water" in name or "river" in name or "stream" in name or "pond" in name or "spill" in name or "foam" in name:
            report["water_related"].append(object_entry(o))
        elif "terrain" in name or "island" in name:
            report["terrain_related"].append(object_entry(o))
        elif "bridge" in name:
            report["bridge_related"].append(object_entry(o))
    for name in ("WATER_Pond","WATER_Stream","WATER_Waterfall","WATER_EdgeSpill",
                 "WP2_River_Continuous","WP2_Waterfall_Unbroken","WP2_Pool_Connector",
                 "TERRAIN_Island_Top","TERRAIN_Island_Underside",
                 "BRIDGE_Wooden_Single","CAMP_Campfire","CLIFF_Waterfall_Rock"):
        o=bpy.data.objects.get(name)
        if o:
            report["landmarks"][name]=object_entry(o)
        else:
            report["warnings"].append("Expected landmark missing: "+name)
    terrain=bpy.data.objects.get("TERRAIN_Island_Top")
    if terrain and terrain.type=="MESH":
        bounds=world_bounds(terrain)
        a,b=bounds["min"],bounds["max"]
        for yi in range(31):
            row=[]
            y=a[1]+(b[1]-a[1])*yi/30
            for xi in range(31):
                x=a[0]+(b[0]-a[0])*xi/30
                row.append(ray_terrain(terrain,x,y))
            report["terrain_grid"].append(row)
        report["terrain_grid_bounds_xy"]=[[a[0],a[1]],[b[0],b[1]]]
    folder=os.path.join(root,"documentation","inspections")
    os.makedirs(folder,exist_ok=True)
    path=os.path.join(folder,"WhisperingPines_WaterGeometry_Report.json")
    with open(path,"w",encoding="utf-8") as f:
        json.dump(report,f,indent=2)
    print("WATER INSPECTION REPORT:",path)
    print("WATER OBJECTS:",len(report["water_related"]))
    print("TERRAIN OBJECTS:",len(report["terrain_related"]))
    print("BRIDGE OBJECTS:",len(report["bridge_related"]))
    print("NO .BLEND FILES WERE MODIFIED.")

if __name__=="__main__":
    main()
