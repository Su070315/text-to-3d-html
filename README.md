# text-to-3d-html

一个 CodeBuddy 技能（Skill）：**根据一段文字描述，生成一个可在浏览器双击打开的 3D 模型**（程序化 Three.js 单文件 HTML）。

无需 GPU、无需 API key、离线可用。灵感来自抖音「月华墅」那类作品——本质是 AI 写 Three.js 代码实时生成建筑/场景，而不是图片转 3D。

## 能力

- 环绕查看 / 缩放 / 平移
- 楼层切换（上方楼层丝滑滑出，每层可看内部布局）
- 白天 / 夜晚切换（窗户暖光、路灯）
- 可编辑模式（点选 / 拖动 / 旋转 / 缩放 / 删除 / 面板添加物体）
- 导出 GLB，可导入 Blender 二次加工

## 目录结构

```
text-to-3d-html/
├── SKILL.md                  # 生成工作流（6 步）
├── references/
│   └── design-guide.md       # 几何助手 + 参数化套路 + 避坑清单
├── scripts/
│   ├── assemble.js           # 组装 app.js + 库 → 单文件 HTML
│   └── blender_import.py     # GLB → Blender（.blend + 预览渲染）
└── templates/
    ├── shell.html            # HTML 外壳（UI/编辑栏/楼层按钮）
    ├── manor_app.js          # 完整参考模板（四层英式庄园）
    ├── three.min.js          # Three.js r128（MIT）
    ├── OrbitControls.js
    └── GLTFExporter.js
```

## 使用方法

在 CodeBuddy 中描述需求即可自动触发，例如：

> 生成3D模型：一栋现代别墅，两层，带泳池和车库

生成流程：理解描述 → 出设计方案 → 写 app.js（复用 templates/design-guide 的几何助手）→ `node scripts/assemble.js app.js 输出.html` → 交付到桌面。

## 许可证

本项目代码按 MIT 协议发布；`templates/three.min.js` 等为 [Three.js](https://threejs.org/)（MIT）自带文件。
