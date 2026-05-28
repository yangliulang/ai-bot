# Runtime Publish · Git 快照 bundle（规格对齐）

**路径**：`specs/requirements/skill-specs/published/runtime-bundle.json`。

**用途**：`publishRequired` **11** 篇技能的 **§1～§6 全文** + `skillSpecVersion` + `specDigest`，供 **评审对账** 与 **所内 MR-B1 import 参考**。**非** 运行时第二 SSOT（编辑仍只在 Git `**/*.md`）。

**层级**：**规格对齐** — 见 [`requirements-closure` §3.6](../requirements-closure.md#36-runtime-publish--原型与规格对齐非生产实现)。**不等于** 生产 DB 已落库。

**生成**（仓库根目录）：

```bash
node specs/requirements/skill-specs/scripts/build_runtime_publish_bundle.mjs
node specs/requirements/skill-specs/scripts/build_runtime_publish_bundle.mjs --check
```

**同窗**：[`PUBLISH.md`](../PUBLISH.md) · [`MR-B-BFF-IMPLEMENTATION.md`](../MR-B-BFF-IMPLEMENTATION.md) · CI [`skill-contract-consistency.yml`](../../../.github/workflows/skill-contract-consistency.yml)。
