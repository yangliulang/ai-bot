interface PlaceholderProps {
  title: string;
  moduleNo: string;
  specPath: string;
}

export function ModulePlaceholder({ title, moduleNo, specPath }: PlaceholderProps) {
  return (
    <>
      <h1 className="page-title">
        {moduleNo} · {title}
      </h1>
      <p className="page-desc">
        演示占位页。规格路径：<code>{specPath}</code>
      </p>
      <div className="card">
        <p style={{ margin: 0, color: "var(--muted)" }}>
          竖切优先完成<strong>运行运营 / AI 治理</strong>与<strong>全局参数</strong>；本页后续可按{" "}
          <code>functions.md</code> 展开表单与列表。
        </p>
      </div>
    </>
  );
}
