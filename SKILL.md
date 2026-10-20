---
name: "text-to-3d-html"
version: "1.0.0"
display_name: "文字生成3D模型(HTML)"
display_name_en: "Text-to-3D HTML Model Generator"
description: "根据用户的一段文字描述，生成一个可双击在浏览器打开的 3D 模型(程序化 Three.js 单文件 HTML)。支持环绕查看、楼层切换、日夜切换、可编辑(添加/移动/删除物体)、导出 GLB 进 Blender。适用于生成一个3D模型、做个房子/建筑/场景、帮我建个别墅/庭院/街区等请求。"
description_zh: "根据用户的一段文字描述，生成一个可双击在浏览器打开的 3D 模型(程序化 Three.js 单文件 HTML)。支持环绕查看、楼层切换、日夜切换、可编辑(添加/移动/删除物体)、导出 GLB 进 Blender。适用于生成一个3D模型、做个房子/建筑/场景、帮我建个别墅/庭院/街区等请求。"
description_en: "Generate a 3D model openable in the browser by double-clicking, from a text description (procedural Three.js single-file HTML). Supports orbit view, floor switching, day/night, editing, and GLB export to Blender."
---
# 文字生成 3D 模型（HTML）

根据用户描述，用程序化 Three.js 代码生成一个单文件 HTML，双击即在浏览器打开。这是复刻抖音月华墅那类作品的正确做法（DeepSeek 写 Three.js 代码），不需要 GPU、不需要 API key、离线可开。

## 完整工作流（严格按顺序）

1. 理解描述 → 提炼：建筑风格、层数、每层功能、外景元素、主色调、布局
2. 先文字出设计方案（尺寸、分组、每层布局），简短列出即可，再动手写代码
3. 写 app.js：以 templates/manor_app.js 为骨架，复用 references/design-guide.md 里的几何助手，按描述改造建筑和布局
4. 组装 HTML：node scripts/assemble.js app.js 输出.html
5. 测试：用 playwright-cli 打开截图 + console 检查；重点验证俯视楼层无遮挡、屋顶贴合、无 NaN 几何
6. 交付：HTML 放桌面；如需进 Blender，页面点导出 GLB 再用 scripts/blender_import.py 转 .blend

## 交互功能骨架（manor_app.js 已内置，新模型直接沿用）

- 轨道控制、日夜切换、自动旋转
- 楼层切换：FLOOR_GROUPS + MODE_SLIDES 通用「上方楼层滑出」机制 + 相机缓动
- 编辑模式：点选/拖动/旋转/缩放/删除 + 面板添加物体
- 导出 GLB：复位所有楼层位置后 parse

## 必守的坑

- 几何体先 geometry.rotateY 烘焙旋转、再 scale（否则菱形屋面）
- 俯视楼层平面：楼板/腰线用边框或墙板，不要用实心盒，否则盖住室内
- 工厂函数必须给默认参数（undefined 会产出 NaN 几何，导出 GLB 会被 Blender 拒绝）
- 导出前复位所有楼层位置
- 组装用 shell.html（含编辑栏），app.js 里可改 document.title 和 #modelTitle
- 楼层数不是 4 时隐藏多余楼层按钮
- Blender 渲染发灰：blender_import.py 已设 view_transform=Standard + 世界背景强度 0.25

## 设计必须原创

参考他人作品只借鉴类型和技术手法，具体造型/配色/命名/布局必须原创（用户明确要求）。

## 交付物

- 桌面 HTML（双击开）+ 可选 GLB 和 .blend（Blender）
- 用一句话说明改了什么、怎么打开
