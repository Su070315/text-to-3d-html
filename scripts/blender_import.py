# -*- coding: utf-8 -*-
"""
AI 图片转 3D 工作流 —— Blender 导入与输出脚本
用法: blender -b --factory-startup --python blender_import.py -- <input.glb> <output_dir> [--no-render]
功能: 导入 GLB -> 规范化缩放/居中 -> 打光 -> 保存 .blend -> Cycles CPU 渲染预览
"""
import bpy
import os
import sys
import math
from mathutils import Vector

def log(msg):
    print("[A3D]", msg, flush=True)

def parse_args():
    # blender -b --python script.py -- input.glb outdir
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    glb = argv[0] if len(argv) > 0 else None
    outdir = argv[1] if len(argv) > 1 else os.path.dirname(glb)
    do_render = "--no-render" not in argv
    return glb, outdir, do_render

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # 清除默认相机/灯光/材质
    for block in list(bpy.data.cameras):
        bpy.data.cameras.remove(block)
    for block in list(bpy.data.lights):
        bpy.data.lights.remove(block)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)

def import_glb(path):
    bpy.ops.import_scene.gltf(filepath=path)
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise RuntimeError("GLB 中未找到网格对象")
    return meshes

def normalize(meshes):
    # 计算所有网格的世界包围盒
    bpy.context.view_layer.update()
    min_c = Vector((1e9, 1e9, 1e9))
    max_c = Vector((-1e9, -1e9, -1e9))
    for o in meshes:
        for corner in o.bound_box:
            wc = o.matrix_world @ Vector(corner)
            min_c.x = min(min_c.x, wc.x); min_c.y = min(min_c.y, wc.y); min_c.z = min(min_c.z, wc.z)
            max_c.x = max(max_c.x, wc.x); max_c.y = max(max_c.y, wc.y); max_c.z = max(max_c.z, wc.z)
    center = (min_c + max_c) / 2
    dims = max_c - min_c
    max_dim = max(dims.x, dims.y, dims.z)
    if max_dim <= 0:
        max_dim = 1.0
    target = 2.0  # 归一化到约 2 单位
    scale = target / max_dim
    for o in meshes:
        # 平移到底部贴地 + 中心对齐
        o.location -= Vector((center.x, center.y, min_c.z))
    for o in meshes:
        o.scale *= scale
    bpy.context.view_layer.update()
    log(f"归一化: max_dim={max_dim:.3f} -> scale={scale:.3f}, 居中并贴地")
    # 返回新的中心高度用于打相机
    return scale


def fix_materials(meshes):
    """修复 AI 生成 GLB 的常见材质问题: metallic=1 且无贴图导致全黑"""
    import bpy
    for o in meshes:
        for slot in o.material_slots:
            mat = slot.material
            if not mat or not mat.use_nodes or not mat.node_tree:
                continue
            for node in mat.node_tree.nodes:
                if node.type != 'BSDF_PRINCIPLED':
                    continue
                base = node.inputs.get("Base Color")
                metal = node.inputs.get("Metallic")
                base_has_tex = base and base.is_linked
                if metal and not metal.is_linked and metal.default_value >= 0.95 and not base_has_tex:
                    metal.default_value = 0.0
                    log(f"  修复材质 metallic: {mat.name}")
                rough = node.inputs.get("Roughness")
                if rough and not rough.is_linked and rough.default_value < 0.05:
                    rough.default_value = 0.5
                    log(f"  修复材质 roughness: {mat.name}")

def setup_world():
    world = bpy.data.worlds.new("A3D_World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.75, 0.85, 0.95, 1.0)
        bg.inputs[1].default_value = 0.25  # 浅灰白背景

def setup_lights():
    # 太阳光
    sun_data = bpy.data.lights.new("A3D_Sun", type='SUN')
    sun_data.energy = 4.5
    sun_obj = bpy.data.objects.new("A3D_Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(55), math.radians(10), math.radians(35))
    # 补光
    area_data = bpy.data.lights.new("A3D_Fill", type='AREA')
    area_data.energy = 120.0
    area_data.size = 4.0
    area_obj = bpy.data.objects.new("A3D_Fill", area_data)
    bpy.context.collection.objects.link(area_obj)
    area_obj.location = (-3, -3, 4)
    area_obj.rotation_euler = (math.radians(45), 0, math.radians(45))

def setup_camera():
    cam_data = bpy.data.cameras.new("A3D_Cam")
    cam_data.lens = 50
    cam_obj = bpy.data.objects.new("A3D_Cam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    # 3/4 视角，围绕原点，距离约 5
    cam_obj.location = (2.7, -3.1, 2.0)
    bpy.context.scene.camera = cam_obj
    # 对准原点
    dir_vec = Vector((0, 0, 0.55)) - cam_obj.location
    cam_obj.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()

def setup_render(outdir, do_render):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.device = 'CPU'
    scene.view_settings.view_transform = 'Standard'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    scene.render.filepath = os.path.join(outdir, "preview.png")
    if do_render:
        log("渲染预览 (Cycles CPU) ...")
        bpy.ops.render.render(write_still=True)
        log("预览已保存: " + scene.render.filepath)

def main():
    glb, outdir, do_render = parse_args()
    if not glb or not os.path.isfile(glb):
        raise SystemExit("用法: -- <input.glb> <output_dir> [--no-render]")
    os.makedirs(outdir, exist_ok=True)
    log(f"导入: {glb}")
    clear_scene()
    meshes = import_glb(glb)
    log(f"找到 {len(meshes)} 个网格对象")
    normalize(meshes)
    fix_materials(meshes)
    setup_world()
    setup_lights()
    setup_camera()
    # 保存 .blend
    blend_path = os.path.join(outdir, "model.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    log("已保存 .blend: " + blend_path)
    setup_render(outdir, do_render)
    log("完成")

if __name__ == "__main__":
    main()
