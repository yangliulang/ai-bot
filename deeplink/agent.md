# AI 协作约定 · Deeplink / H5

本目录为 **C 端** 工程，与 `admin/`（运营控制台）并列；职责边界见仓库根目录若存在的 `agent.md` 与 **`README.md`**。

## 强制优先阅读

1. **`docs/前端开发规范.md`**（本目录摘要，完整条文见 `../admin/docs/前端开发规范.md`）
2. **`product-doc/specs/requirements/integrations/telegram/deeplink.md`**（相对 monorepo 根路径）

## 禁止

- **臆造** 未在 product-doc / OpenAPI 冻结的域名、查询参数、payload 格式
- 在防钓鱼文案中写死未经产品确认的「官方域名」列举（宜用原则性话术 + SSOT）

## 文件头留痕

与 `admin` 一致：新建/变更 Vue/TS 源码须在文件首部注明作者、日期、修改功能。
