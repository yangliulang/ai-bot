import type { SkillPublishProblem } from "../api/types/skillOperationSpec";

export class SkillPublishError extends Error {
  constructor(
    public readonly code: NonNullable<SkillPublishProblem["code"]>,
    message: string,
    public readonly status = 400,
  ) {
    super(message);
    this.name = "SkillPublishError";
  }

  toProblem(): SkillPublishProblem {
    return {
      type: `urn:coobit:skill-publish:${this.code}`,
      title: this.code,
      detail: this.message,
      code: this.code,
    };
  }
}
