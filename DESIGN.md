---
name: ChainUp AI Agent Admin
colors:
  bg_base: '#020617'
  bg_surface: '#0f172a'
  bg_panel: '#020617'
  border_subtle: '#1e293b'
  text_primary: '#f8fafc'
  text_secondary: '#94a3b8'
  text_muted: '#64748b'
  accent: '#34d399'
  accent_hover: '#10b981'
  danger: '#f43f5e'
  warning: '#fbbf24'

typography:
  font_sans: Geist Variable
  font_mono: Geist Mono Variable
  heading:
    fontFamily: Geist Variable
    fontWeight: 600
    letterSpacing: '-0.02em'
  body:
    fontFamily: Geist Variable
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.5

rounded:
  ui: 8px
  ui_lg: 12px

spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  section: 32px

components:
  button_primary:
    backgroundColor: '{colors.accent}'
    textColor: '{colors.bg_base}'
    rounded: '{rounded.ui}'
    padding: '10px 14px'
    fontWeight: 500
  button_secondary:
    backgroundColor: '{colors.bg_surface}'
    textColor: '{colors.text_primary}'
    borderColor: '{colors.border_subtle}'
    rounded: '{rounded.ui}'
    padding: '10px 14px'
  input_field:
    backgroundColor: '{colors.bg_base}'
    textColor: '{colors.text_primary}'
    borderColor: '{colors.border_subtle}'
    rounded: '{rounded.ui}'
    height: 40px
    paddingX: 12px
    focusRing: '{colors.accent}'
---

## Overview

控制台面向运营与运维：**深色、低噪、单点强调色**，避免「霓虹紫」类通用 AI 配色。信息密度中等：列表与表单可读优先，关键操作用 **emerald** 引导，破坏性操作用 **danger**。

## Colors

- **bg_base / bg_surface**：页面与侧栏分层，保持 slate 家族内对比。  
- **accent**：唯一主交互色（主按钮、选中态、关键链接）；与 `admin` 侧栏 nav active 一致。  
- **danger**：删除、不可逆确认（如删除 Webhook）。

## Typography

- 全站 UI 使用 **Geist / Geist Mono**（见 `admin` 字体加载）。  
- 标题略紧字距；正文 `text-sm` 层级与现有 `UiInput`/`UiButton` 对齐。

## Layout

- 主内容 **max-width**：与 `AdminLayout` 中 `max-w-7xl` 一致思路。  
- 全高布局使用 **`min-h-[100dvh]`** 而非 `100vh`（移动端地址栏）。

## Elevation & Depth

- 少用重阴影；侧栏/顶栏可用 **细内描边 + backdrop-blur** 表达层次。

## Shapes

- 控件圆角统一 **`{rounded.ui}`**；大容器可用 **`{rounded.ui_lg}`**。

## Components

- **Primary button**：`{components.button_primary}`。  
- **Secondary / ghost**：见 `button_secondary`；ghost 无边线时以 hover 底表达。  
- **Input**：固定行高 40px，与 `UiButton` **md** 尺寸对齐。

## Do's and Don'ts

- **Do**：改色板时先改 YAML，再同步 Tailwind/组件；跑 `npx @google/design.md lint DESIGN.md`。  
- **Don't**：在控制台文案中引入未在产品文档出现的 **外链域名**（deeplink 以 `product-doc` 为准）。  
- **Don't**：用 emoji 作 UI 图标替代物（与前端工程约定一致）。
