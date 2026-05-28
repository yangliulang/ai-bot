import { Divider, Typography } from "antd";

const { Text, Paragraph } = Typography;

/** 人类可读：对应 specs/requirements/ 下的相对路径 */
export function SpecFooter({ paths, compact }: { paths: string[]; compact?: boolean }) {
  return (
    <footer style={{ marginTop: compact ? 0 : 32 }}>
      <Divider style={{ margin: compact ? "8px 0" : "16px 0" }} />
      <Paragraph type="secondary" style={{ marginBottom: 8, fontSize: 12 }}>
        以下为<strong>仓库内规格文件</strong>索引（便于研发对照；运营可忽略）。
      </Paragraph>
      <ul style={{ margin: 0, paddingLeft: 20, fontSize: 12, color: "rgba(0,0,0,0.45)" }}>
        {paths.map((p) => (
          <li key={p}>
            规格路径：<Text code>规格要求/{p}</Text>
          </li>
        ))}
      </ul>
    </footer>
  );
}
