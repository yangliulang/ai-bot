import { Typography } from "antd";

const { Paragraph } = Typography;

type Props = {
  title: string;
  hint?: string;
};

/** H5 占位页：行情 / 合约等与交易所主导航对齐，内容为示意 */
export default function H5PlaceholderPage({ title, hint = "示意页面 · 正式功能以 Coolbit App / H5 为准" }: Props) {
  return (
    <div className="coolbit-h5-placeholder">
      <h1 className="coolbit-page-title" style={{ marginBottom: 12 }}>
        {title}
      </h1>
      <Paragraph type="secondary" style={{ marginBottom: 0 }}>
        {hint}
      </Paragraph>
    </div>
  );
}
