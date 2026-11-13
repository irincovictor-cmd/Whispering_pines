"""Water Phase 2 prototype for Blender 5.x. Uses existing WhisperingPines_Main.blend.
Archives old water objects; backs up scene before saving under same filename.
"""
import bpy, math, json, os, shutil
from mathutils import Vector

MAIN = "WhisperingPines_Main.blend"
WATER_NAMES = ("WATER_Stream", "WATER_Pond", "WATER_Waterfall", "WATER_EdgeSpill")
NEW_COLL = "WP2_Continuous_Water"
OLD_COLL = "WP2_Original_Water_Archive"

def lerp(a,b,t):
    return a*(1-t)+b*t

def bezier(a,b,c,d,t):
    q=1-t
    return a*q**3+3*b*q*q*t+3*c*q*t*t+d*t**3

def collection(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def material(name,rgba):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    n=m.node_tree.nodes
    bsdf=n.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value=rgba
    bsdf.inputs["Roughness"].default_value=.21
    noise=n.new("ShaderNodeTexNoise")
    noise.noise_dimensions="4D"
    noise.inputs["Scale"].default_value=9
    noise.inputs["W"].driver_add("default_value").driver.expression="frame * .016"
    ramp=n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color=(rgba[0]*.65,rgba[1]*.78,rgba[2]*.83,1)
    ramp.color_ramp.elements[1].color=rgba
    m.node_tree.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    m.node_tree.links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
    return m

def strip(name,points,widths,mat,col):
    vertices=[]
    for i,p in enumerate(points):
        vector=points[min(i+1,len(points)-1)]-points[max(i-1,0)]
        vector.z=0
        if vector.length<.0001: vector=Vector((0,-1,0))
        vector.normalize()
        side=Vector((-vector.y,vector.x,0))
        vertices.extend((tuple(p-side*widths[i]/2),tuple(p+side*widths[i]/2)))
    faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(points)-1)]
    mesh=bpy.data.meshes.new(name+"_Mesh")
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    col.objects.link(ob)
    ob.data.materials.append(mat)
    return ob

def terrain_z(terrain,x,y):
    inv=terrain.matrix_world.inverted_safe()
    origin=inv@Vector((x,y,1000))
    direction=(inv.to_3x3()@Vector((0,0,-1))).normalized()
    ok,local,_,_=terrain.ray_cast(origin,direction,distance=2200)
    return (terrain.matrix_world@local).z if ok else None

def main():
    filepath=os.path.abspath(bpy.data.filepath)
    if os.path.basename(filepath)!=MAIN or os.path.basename(os.path.dirname(filepath)).lower()!="blender":
        raise RuntimeError("Open blender/"+MAIN+" before running water Phase 2.")
    if bpy.data.collections.get(NEW_COLL):
        raise RuntimeError("Phase 2 already applied; use the pre-water checkpoint to retry.")
    objects={n:bpy.data.objects.get(n) for n in (*WATER_NAMES,"TERRAIN_Island_Top","BRIDGE_Wooden_Single")}
    if any(objects[n] is None for n in ("WATER_Pond","WATER_Waterfall","WATER_Stream","TERRAIN_Island_Top","BRIDGE_Wooden_Single")):
        raise RuntimeError("Required water, terrain or bridge landmark missing.")
    top=objects["TERRAIN_Island_Top"]
    bridge=objects["BRIDGE_Wooden_Single"].matrix_world.translation.copy()
    pool=objects["WATER_Pond"].matrix_world.translation.copy()
    fall=objects["WATER_Waterfall"]
    direction=bridge-pool
    direction.z=0
    if direction.length<.01:
        raise RuntimeError("Bridge and pond overlap; cannot determine river direction.")
    direction.normalize()
    vertices=[top.matrix_world@v.co for v in top.data.vertices]
    extent=max(max(v.x for v in vertices)-min(v.x for v in vertices),
               max(v.y for v in vertices)-min(v.y for v in vertices))
    # Move from bridge along river direction until outside main terrain.
    last=None
    for i in range(1,151):
        p=bridge+direction*(extent*.012*i)
        if terrain_z(top,p.x,p.y) is None: break
        last=p
    if last is None or (last-bridge).length<extent*.12:
        raise RuntimeError("Could not find safe outlet; inspect river/bridge orientation.")
    outlet=last+direction*(extent*.008)
    outlet.z=0
    source=Vector((pool.x,pool.y,0))
    crossing=Vector((bridge.x,bridge.y,0))
    side=Vector((-direction.y,direction.x,0))
    span=(outlet-source).length
    bend=side*extent*.055
    path=[bezier(source,source+direction*span*.13,crossing-direction*span*.09+bend,crossing,i/26) for i in range(27)]
    path.extend(bezier(crossing,crossing+direction*span*.15-bend,
                       outlet-direction*span*.17+bend*.3,outlet,i/35) for i in range(1,36))
    heights=[]
    missed=0
    for p in path:
        z=terrain_z(top,p.x,p.y)
        if z is None:
            missed+=1
            z=heights[-1] if heights else pool.z
        heights.append(z)
    uphill=sum(1 for a,b in zip(heights,heights[1:]) if b>a+.1)
    # Clamp surface to non-increasing downstream; never force flow uphill.
    centerline=[]
    height=heights[0]+.075
    for p,z in zip(path,heights):
        height=min(height,z+.075)
        centerline.append(Vector((p.x,p.y,height)))
    width=max(.65,min(2.6,extent*.066))
    new=collection(NEW_COLL)
    old=collection(OLD_COLL)
    water=material("WP2_Animated_Water",(0.11,.54,.78,1))
    foam=material("WP2_Water_Foam",(.73,.93,1.,1.))
    widths=[width*(.86+.14*math.sin(math.pi*i/(len(centerline)-1))) for i in range(len(centerline))]
    strip("WP2_River_Continuous",centerline,widths,water,new)
    # Fall: one full vertical ribbon from upper waterfall edge to lower pool.
    fverts=[fall.matrix_world@Vector(v) for v in fall.bound_box]
    topz=max(v.z for v in fverts)
    bottomz=min(v.z for v in fverts)
    if topz-bottomz<.3: topz=bottomz+max(1,extent*.1)
    tip=fall.matrix_world.translation.copy()
    flow=[]
    for i in range(33):
        t=i/32
        flow.append(Vector((tip.x+direction.x*(topz-bottomz)*.09*t*t,
                            tip.y+direction.y*(topz-bottomz)*.09*t*t,
                            lerp(topz,max(bottomz,centerline[0].z-.09),t))))
    strip("WP2_Waterfall_Unbroken",flow,[width*.72]*len(flow),water,new)
    strip("WP2_Waterfall_Whitewater",[p+Vector((0,0,.018)) for p in flow[16:]],
          [width*.30]*len(flow[16:]),foam,new)
    # Horizontal feed between fall bottom and river source prevents visible open gap.
    feed_start=flow[-1]
    feed_end=centerline[0]
    feed=[lerp(feed_start,feed_end,i/18) for i in range(19)]
    strip("WP2_Pool_Connector",feed,[width*(.7+.2*math.sin(math.pi*i/18)) for i in range(19)],water,new)
    archive=[]
    for name in WATER_NAMES:
        obj=objects.get(name)
        if obj:
            for c in tuple(obj.users_collection): c.objects.unlink(obj)
            old.objects.link(obj)
            obj.hide_render=True
            obj.hide_set(True)
            archive.append(name)
    old.hide_render=True
    backup_dir=os.path.join(os.path.dirname(filepath),"checkpoints")
    os.makedirs(backup_dir,exist_ok=True)
    backup=os.path.join(backup_dir,"WhisperingPines_PreWater_Phase1B.blend")
    if not os.path.exists(backup): shutil.copy2(filepath,backup)
    report={"working_file":filepath,"backup":backup,"archived":archive,
            "new_collection":NEW_COLL,"river_terrain_misses":missed,
            "uphill_segments_detected":uphill,
            "warnings":["River terrain is NOT carved. A surface may clip or float.",
                        "New river should be inspected under bridge and at cliff edge.",
                        "This uses animated shader noise, not fluid simulation.",
                        "Check vertical fall-to-pool connection in material preview."]}
    with open(os.path.join(os.path.dirname(filepath),"WhisperingPines_Phase2_Water_Report.json"),"w",encoding="utf-8") as f:
        json.dump(report,f,indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=filepath,compress=True)
    print("PHASE 2 WATER SAVED TO",filepath)
    print("BACKUP",backup)
    print("TERRAIN MISSING HITS:",missed,"UPHILL SECTIONS:",uphill)

if __name__=="__main__":
    main()
