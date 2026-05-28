# 定位 · 愿景（Positioning）

本篇是 **`product/`** 叙事：**方向感与对外一句话**，不向本文写入 FR/SC。验收与门禁仍以 **[`specs/requirements/product.md`](../specs/requirements/product.md)** 与各 **`domains/`**、`flows/` 为准。**可对签 vs 剩余关单**：[`contract-closure.md`](../specs/requirements/contract-closure.md) **DoD**；[**`closure-remaining` §7～§7.6**](../specs/requirements/closure-remaining.md#closure-remaining-quicklinks)（**本仓 vs 所内 · MR**）。

## 我们想成为什么

在 **单一交易所（Coobit）× 会话渠道（本版 Telegram）** 前提下，让用户用自然语言可靠地完成：**行情与账户可读、在满足矩阵与确认为前提下的可写自动化与交易相关工作**，并让 **计费、审计、可追溯** 可运营、可对账。

## 坚持什么

- **安全与门禁优先**：每笔 Coobit 写路径遵守 **ADR-001**（[**Telegram「类型 A」确认闸门先于 Coobit 写**](../specs/design/adr/001-telegram-confirm-before-coobit-write.md)）与 **`exchange-agent` / `trade-assistance`** 中的矩阵与 **`toolId`** 约定。
- **契约不夸大**：产品上可承诺的执行集以 **[`specs/design/api.md`](../specs/design/api.md)** 已冻结矩阵为上限；未见于矩阵的能力在对外沟通中默认为 **不提供 / 待定**。**剩余关单 · MR 勾选** → [`closure-remaining` §7.5](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path) · [§7.6](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)（**与** **篇首双表** **对读**）。
- **叙事与契约分离**：本目录不写技术栈与排期；实现与接口见 **`specs/design/`**。

## 相关阅读

- [产品概览与范围](./overview.md)
- [关键用户路径](./flows.md)
- [用户场景提要](./user-scenarios.md)
- [里程碑](./milestones.md)
- [路线图](./roadmap.md)
- [本目录文档地图](./README.md#本目录文档地图)

## 我们**不**对外暗示的事

- **矩阵未冻或标 TBD** 的交易所能力 ≠ 用户一定能「在 Telegram 里点确认就闭环」。
- **自然语言** 不等于可以 **跳过类型 A** 或对 **多笔写** 做「一包确认」— 见 [`telegram-and-cards.md`](./telegram-and-cards.md)。
- **`product/`** 里的排期、人力、技术栈 **不是** SSOT；执行节奏以 [`roadmap.md`](./roadmap.md) 叙述为准，契约以 **`specs/`** 为准。
