import { Navigate } from "react-router-dom";

/** 旧路径重定向 → /subaccount/billing（账单与消耗） */
export default function BillingSummaryStubPage() {
  return <Navigate to="/subaccount/billing" replace />;
}
