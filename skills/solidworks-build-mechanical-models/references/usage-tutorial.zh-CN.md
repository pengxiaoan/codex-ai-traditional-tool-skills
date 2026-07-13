# 使用教程（中文）

## 1. 安装 Skill

将整个 `solidworks-build-mechanical-models` 文件夹复制到：

```text
%USERPROFILE%\.codex\skills\solidworks-build-mechanical-models
```

重新启动 Codex 会话，使 Skill 出现在可用技能列表中。也可以从 GitHub 克隆后，用 `skill-installer` 安装仓库中的 Skill 路径。

## 2. 适用请求

可直接使用类似提示：

```text
使用 $solidworks-build-mechanical-models，在 SolidWorks 中绘制一套双摆线盘减速机构。
要求生成可编辑 SLDPRT/SLDASM、完整建模录屏、最终等轴测预览和构建日志。
外壳直径 172 mm，18 根针齿销，双盘相位差 180/17 度；未指定尺寸可作为概念假设，但必须列出。
```

也可用于已有图纸或图片：

```text
使用 $solidworks-build-mechanical-models，根据附件机械图重建装配体。
图纸标注尺寸优先于图片比例；输出零件、装配、配合说明和验收报告。
```

## 3. 建议提供的信息

- SolidWorks 版本；
- 关键尺寸、单位和公差；
- 零件数量及装配关系；
- 是否需要运动、配合、干涉检查；
- 是否需要全过程录屏、分辨率和帧率；
- 交付格式：SLDPRT、SLDASM、STEP、预览图、MP4；
- 模型属于概念展示、工程布局还是生产设计。

信息不足时，Skill 会先建立参数表并区分“权威尺寸”和“概念假设”。

## 4. 三种工作方式

### GUI 建模

适合复杂曲面、放样、交互调整和需要人工检查设计意图的模型。

### API 自动建模

适合圆柱、孔阵列、重复零件、参数化零件和需要可重复录制的任务。API 输入长度使用米，Skill 会在参数边界统一换算。

### 混合建模

先用 API 生成零件和装配结构，再在 GUI 中检查配合、外观、剖视和最终视图。复杂机械结构和完整录屏通常优先使用此方式。

## 5. 交付结果

标准交付目录包含：

```text
output/
  main.SLDASM
  01_part.SLDPRT
  02_part.SLDPRT
  build_log.txt
  final_preview.png
  modeling_process.mp4
  builder.vbs
```

交付说明必须写明：SolidWorks 版本、零件/组件数量、录屏规格、模型状态以及未验证的载荷、材料、公差或制造假设。

## 6. 验收命令

在 Skill 目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-delivery.ps1 `
  -OutputDirectory C:\project\output `
  -Assembly C:\project\output\main.SLDASM `
  -ExpectedPartCount 10 `
  -Video C:\project\output\modeling_process.mp4 `
  -RequireBuildComplete
```

脚本通过后，仍需在 SolidWorks 中检查重建状态、零件缺失、装配相位、配合和干涉。
