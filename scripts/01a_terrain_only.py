"""Phase 1A terrain-only reconstruction. Run using Blender 5.x on the ORIGINAL source file."""
import bpy, os, json, math
from collections import defaultdict
from mathutils import Vector

TOP="TERRAIN_Island_Top"
BOTTOM="TERRAIN_Island_Underside"
SOURCE="WhisperingPines_Blockout_v01.blend"
OUTPUT="WhisperingPines_Phase1A_Terrain.blend"

def smooth(t):
    t=max(0.,min(1.,t))
    return t*t*(3-2*t)

def groups(obj):
    parent=list(range(len(obj.data.vertices)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    for edge in obj.data.edges:
        a,b=(find(i) for i in edge.vertices)
        parent[a]=b
    g=defaultdict(list)
    for i in range(len(parent)):
        g[find(i)].append(i)
    result=[]
    for indices in g.values():
        pts=[obj.matrix_world @ obj.data.vertices[i].co for i in indices]
        result.append({"vertices":len(indices),
                       "center":[round(sum(p[j] for p in pts)/len(pts),3) for j in range(3)],
                       "extent":[round(max(p[j] for p in pts)-min(p[j] for p in pts),3) for j in range(3)]})
    return sorted(result,key=lambda x:x["vertices"],reverse=True)

def main():
    original=os.path.abspath(bpy.data.filepath)
    if os.path.basename(original)!=SOURCE or os.path.basename(os.path.dirname(original)).lower()!="source":
        raise RuntimeError("Open repository/source/"+SOURCE+" before running.")
    root=os.path.dirname(os.path.dirname(original))
    folder=os.path.join(root,"blender")
    os.makedirs(folder,exist_ok=True)
    output=os.path.join(folder,OUTPUT)
    if os.path.exists(output):
        raise RuntimeError("Refusing to overwrite existing checkpoint: "+output)
    top=bpy.data.objects.get(TOP)
    bottom=bpy.data.objects.get(BOTTOM)
    if any(o is None or o.type!="MESH" or len(o.data.vertices)<12 for o in (top,bottom)):
        raise RuntimeError("Source terrain top/underside meshes missing or incomplete.")
    report={"source":original,"output":output,"before":{o.name:groups(o) for o in (top,bottom)},
            "removed_objects":[],"moved_other_objects":[],"review":[]}
    for obj in bpy.data.objects:
        n=obj.name.lower().replace("-","_").replace(" ","_")
        if "sub_island" in n or "secondary_island" in n or obj.get("whispering_pines_sub_island",False):
            report["review"].append("Candidate sub-island: "+obj.name+" (not deleted; visually confirm).")
    if any(len(report["before"][o.name])>1 for o in (top,bottom)):
        report["review"].append("Disconnected terrain components detected: inspect centers in report.")
    else:
        report["review"].append("No clearly separate terrain component: do not guess which mesh is sub-island.")
    pts=[top.matrix_world @ v.co for v in top.data.vertices]
    center=Vector(((min(p.x for p in pts)+max(p.x for p in pts))/2,
                   (min(p.y for p in pts)+max(p.y for p in pts))/2,0))
    waterfall=bpy.data.objects.get("CLIFF_Waterfall_Rock")
    campfire=bpy.data.objects.get("CAMP_Campfire")
    front=campfire.matrix_world.translation-waterfall.matrix_world.translation if waterfall and campfire else Vector((0,-1,0))
    front.z=0
    if front.length<.001:
        front=Vector((0,-1,0))
    front.normalize()
    side=Vector((-front.y,front.x,0))
    uv=[((p-center).dot(side),(p-center).dot(front)) for p in pts]
    half_width=max(max(abs(u) for u,v in uv),.01)
    front_reach=max(max(v for u,v in uv),.01)
    rear_reach=max(max(-v for u,v in uv),.01)
    def warp(point):
        relative=point-center
        u,v=relative.dot(side),relative.dot(front)
        horizontal=smooth((abs(u)/half_width-.42)/.58)
        reach=front_reach if v>=0 else rear_reach
        longitudinal=smooth((abs(v)/reach-.42)/.58)
        u*=1+.22*horizontal
        v*=1+(.19 if v>=0 else .02)*longitudinal
        return Vector((center.x+side.x*u+front.x*v,center.y+side.y*u+front.y*v,point.z))
    z_values=[(bottom.matrix_world @ v.co).z for v in bottom.data.vertices]
    zmax,zmin=max(z_values),min(z_values)
    span=max(zmax-zmin,.001)
    for obj in (top,bottom):
        if obj.data.users>1:
            obj.data=obj.data.copy()
        inv=obj.matrix_world.inverted_safe()
        points=[]
        for vertex in obj.data.vertices:
            world=obj.matrix_world @ vertex.co
            updated=warp(world)
            if obj is bottom:
                depth=smooth((zmax-world.z)/span)
                wave=math.sin(world.x*1.47+world.y*.51)*math.cos(world.y*1.13-world.x*.38)
                updated.z-=span*(.08+.045*wave)*depth
            points.append(inv @ updated)
        for vertex,position in zip(obj.data.vertices,points):
            vertex.co=position
        obj.data.update()
        obj["WP_phase1A_terrain_only"]=True
    report["after"]={o.name:groups(o) for o in (top,bottom)}
    report["expansion"]={"sides":.22,"front":.19,"rear":.02,"protected_core":.42}
    report["review"].append("Other objects unchanged; check perimeter grounding, camp clipping, and water intersections.")
    report["review"].append("Sub-island removal requires positive object/component identification.")
    bpy.ops.wm.save_as_mainfile(filepath=output,compress=True)
    with open(os.path.join(folder,"WhisperingPines_Phase1A_report.json"),"w",encoding="utf8") as f:
        json.dump(report,f,indent=2)
    print("PHASE 1A CHECKPOINT:",output)
    print("OTHER OBJECTS MOVED: 0")
    for warning in report["review"]:
        print("REVIEW:",warning)

if __name__=="__main__":
    main()
