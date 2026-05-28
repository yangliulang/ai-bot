-- Skill Operation Spec · MR-B1 存储草案（所内 DDL 终裁）
-- 同窗：specs/requirements/skill-specs/MR-B-BFF-IMPLEMENTATION.md
-- 禁止仅存摘要；body_markdown = Git §1～§6 全文

CREATE TABLE skill_operation_spec_version (
  skill_id            VARCHAR(128)  NOT NULL,
  skill_spec_version  VARCHAR(64)   NOT NULL,
  lifecycle           VARCHAR(16)   NOT NULL DEFAULT 'PUBLISHED'
    CHECK (lifecycle IN ('PUBLISHED', 'DEPRECATED')),
  body_markdown       TEXT          NOT NULL,
  spec_digest         CHAR(64)      NOT NULL,
  published_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  source_git_ref      VARCHAR(256),
  PRIMARY KEY (skill_id, skill_spec_version)
);

CREATE INDEX idx_skill_operation_spec_version_published
  ON skill_operation_spec_version (skill_id, published_at DESC);

CREATE TABLE skill_operation_spec_pointer (
  skill_id            VARCHAR(128)  PRIMARY KEY,
  skill_spec_version  VARCHAR(64)   NOT NULL,
  updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_skill_pointer_version
    FOREIGN KEY (skill_id, skill_spec_version)
    REFERENCES skill_operation_spec_version (skill_id, skill_spec_version)
);

COMMENT ON TABLE skill_operation_spec_version IS 'read_skill_operation_spec 正文快照；Publish 单调版本';
COMMENT ON TABLE skill_operation_spec_pointer IS '每 skillId 当前生效版本（Rollback = 更新指针）';
