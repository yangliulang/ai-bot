/**
 * @deprecated 请使用 `./skillRegistryCatalog`；本文件保留 re-export 以免散落引用。
 */
export {
  countPublishReadySpecs,
  getSkillMarkdown,
  getSkillRegistryEntry as getSkillCatalogEntry,
  parseContractStatus,
  resolveSkillContractStatus,
  SKILL_REGISTRY_ENTRIES as SKILL_SPEC_CATALOG,
  type SkillContractStatus,
  type SkillRegistryEntry as SkillCatalogEntry,
} from "./skillRegistryCatalog";
