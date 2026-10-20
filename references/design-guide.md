# 程序化 3D 模型设计指南

从文字描述生成新模型时，按本指南组织代码。骨架参考 templates/manor_app.js。

## 1. 场景骨架（照抄，改名称即可）

- renderer/camera/OrbitControls/shadowMap
- 灯光：hemi(天光) + sun(主光带阴影) + moon(夜景)
- 材质工厂 M(color, opts)，玻璃数组 glassMats（夜景点亮用）
- 分组：gRoof / gF1..gF4 / gSite，统一挂到根组（导出用）
- 日夜 setNight(v)：切 sun/moon/hemi 强度、背景色、玻璃 emissive、路灯 lampLights
- 楼层切换：FLOOR_GROUPS + MODE_SLIDES（上方楼层滑出）+ tweenVec 缓动
- 编辑模式：点选/拖动（groundPlane 射线）+ FACTORIES 面板
- 导出 GLB：exportBtn 复位所有楼层位置后 exporter.parse

## 2. 几何助手（直接复用）

- box(parent, w,h,d, mat, x,y,z, ry)：长方体
- cyl(parent, rt,rb,h, mat, x,y,z, seg)：圆柱/棱柱
- sph(parent, r, mat, x,y,z)：球
- wallsBox(parent, w,h,d, y, mat, t)：四面墙板（俯视能看到室内，关键！）
- frameBox(parent, w,h,d, y, mat)：四条边框（腰线/檐口用，不盖室内）
- gableRoof(parent, w,d, y0, h, overhang, mat)：山墙屋顶（返回 group 可旋转）
- gableWall(parent, w, y0, h, z, mat, depth)：山墙三角（ExtrudeGeometry）
- windowAt(parent, x,y,z, ry, w,h, arched)：带分格和窗台的窗

## 3. 建筑参数化套路

- 先定楼层高度：Y1、H1..Hn、Y2=Y1+H1、...、YT、EAVE
- 每层：wallsBox 建墙 + 窗口循环 + 层间线(frameBox)
- 屋顶：gableRoof（山墙）/ 孟莎顶(CylinderGeometry 4段 + rotateY 烘焙)
- 凸体/翼楼：单独 wallsBox 时手动给 cx/cz（wallsBox 不支持偏移，别忘！）

## 4. 家具工厂（按需）

bed/wardrobe/nightstand/sofa/chair/desk/rug/pendant 等，都接受楼层 Y 参数。每层布局不同：一层生活区、二层卧室、三层套房、四层娱乐（可自由发挥）。

## 5. 外景

树(makeTree)/灌木/花/石头/长椅/路灯/车/亭子/喷泉工厂 + 花园、池塘、假山、停车场、秋千等。

## 6. 高频坑（务必检查）

1. 屋面棱柱：geometry.rotateY(PI/4) 再 mesh.scale，不要 mesh.rotation.y（菱形屋面）
2. 实心盒盖室内：楼板/腰线/翼楼墙体必须用墙板或边框
3. 工厂函数默认参数：s = s || 1（undefined 会 NaN，导出 GLB 报错）
4. wallsBox 不支持偏移：偏移位置要手动写 4 面墙
5. 导出前复位所有楼层位置
6. 测试用 playwright-cli（file:// 被拦，走本地 http.server）

## 7. 交付检查单

- 双击 HTML 能开、无 console 报错
- 每个楼层俯视能看进室内、有内容
- 屋顶贴合建筑、无漂浮/菱形
- 日夜切换正常、导出 GLB 正常
- 命名/设计原创，不抄别人
