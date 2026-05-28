/** 统一业务 / HTTP 错误模型（单一入口解析后抛出） */
export class AppError extends Error {
  readonly code?: string
  readonly status?: number
  readonly details?: Record<string, unknown>

  constructor(
    message: string,
    options?: { cause?: unknown; code?: string; status?: number; details?: Record<string, unknown> },
  ) {
    super(message, options?.cause ? { cause: options.cause } : undefined)
    this.name = 'AppError'
    this.code = options?.code
    this.status = options?.status
    this.details = options?.details
  }
}
