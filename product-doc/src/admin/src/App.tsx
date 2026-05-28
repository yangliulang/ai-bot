import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ConfirmationRulesProvider } from "./context/ConfirmationRulesContext";
import { OrchestrationPolicyProvider } from "./context/OrchestrationPolicyContext";
import { InstancesPage } from "./pages/agent/InstancesPage";
import { InstanceDetailPage } from "./pages/agent/InstanceDetailPage";
import { PromptSafetyPage, PromptStrategyPage } from "./pages/prompt/PromptPages";
import { PromptPackEditorPage } from "./pages/prompt/PromptPackEditorPage";
import { PromptViewPage } from "./pages/prompt/PromptViewPage";
import { AiSettingsPage } from "./pages/ai/AiSettingsPage";
import { BillingOverviewPage } from "./pages/billing/BillingOverviewPage";
import { BillingLedgerPage } from "./pages/billing/BillingLedgerPage";
import { BillingOperationsPage } from "./pages/billing/BillingOperationsPage";
import {
  BillingCommercePage,
  BillingOrdersPage,
  BillingPacksPage,
  BillingPricingPage,
  BillingSubscriptionsPage,
  BillingUserConsumptionPage,
} from "./pages/billing/billingLegacyRedirects";
import { AccessPage } from "./pages/access/AccessPage";
import { ObservabilityPage } from "./pages/observability/ObservabilityPage";
import { ExecutionListPage } from "./pages/runtime/ExecutionListPage";
import { ExecutionDetailPage } from "./pages/runtime/ExecutionDetailPage";
import { ConfirmationRuleEditorPage } from "./pages/governance/confirmation/ConfirmationRuleEditorPage";
import { ConfirmationRulesPage } from "./pages/governance/ConfirmationRulesPage";
import { RuntimeOrchestrationPage } from "./pages/governance/RuntimeOrchestrationPage";
import { ChannelConfigPage } from "./pages/system/ChannelConfigPage";
import { ToolRegistryPage } from "./pages/tools/ToolRegistryPage";

function HomeRedirect() {
  return <Navigate to="/runtime/executions" replace />;
}

/** 旧书签：原智能体配置 / 模板路由已移除，统一落到实例列表 */
function LegacyAgentsConfigRedirect() {
  return <Navigate to="/agents/instances" replace />;
}

export default function App() {
  return (
    <OrchestrationPolicyProvider>
      <ConfirmationRulesProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
          <Route index element={<HomeRedirect />} />
          <Route path="runtime/executions" element={<ExecutionListPage />} />
          <Route path="runtime/executions/:executionId" element={<ExecutionDetailPage />} />
          <Route path="runtime/tasks" element={<Navigate to="/runtime/executions" replace />} />
          <Route path="runtime/events" element={<Navigate to="/runtime/executions" replace />} />
          <Route path="agents/config" element={<LegacyAgentsConfigRedirect />} />
          <Route path="agents/config/:configId" element={<LegacyAgentsConfigRedirect />} />
          <Route path="agents/templates" element={<LegacyAgentsConfigRedirect />} />
          <Route path="agents/templates/:templateId" element={<LegacyAgentsConfigRedirect />} />
          <Route path="agents/instances" element={<InstancesPage />} />
          <Route path="agents/instances/:instanceId" element={<InstanceDetailPage />} />
          <Route path="prompts" element={<Navigate to="/prompts/strategy" replace />} />
          <Route path="prompts/strategy" element={<PromptStrategyPage />} />
          <Route path="prompts/system" element={<Navigate to="/prompts/strategy" replace />} />
          <Route path="prompts/scenarios" element={<Navigate to="/prompts/strategy" replace />} />
          <Route path="prompts/safety" element={<PromptSafetyPage />} />
          <Route path="prompts/view/:promptPackId" element={<PromptViewPage />} />
          <Route path="prompts/editor/:promptPackId" element={<PromptPackEditorPage />} />
          <Route path="ai/runtime-orchestration" element={<RuntimeOrchestrationPage />} />
          <Route path="ai/tool-registry" element={<ToolRegistryPage />} />
          <Route path="ai/skill-specs" element={<Navigate to="/ai/tool-registry" replace />} />
          <Route path="tools/registry" element={<Navigate to="/ai/tool-registry" replace />} />
          <Route path="tools" element={<Navigate to="/ai/tool-registry" replace />} />
          <Route path="ai/tool-policies" element={<Navigate to="/ai/tool-registry" replace />} />
          <Route path="ai/confirmation-rules" element={<ConfirmationRulesPage />} />
          <Route path="ai/confirmation-rules/new" element={<ConfirmationRuleEditorPage mode="create" />} />
          <Route path="ai/confirmation-rules/edit/:ruleId" element={<ConfirmationRuleEditorPage mode="edit" />} />
          <Route path="ai-settings" element={<AiSettingsPage />} />
          <Route path="billing" element={<Navigate to="/billing/overview" replace />} />
          <Route path="billing/overview" element={<BillingOverviewPage />} />
          <Route path="billing/pricing" element={<BillingPricingPage />} />
          <Route path="billing/operations" element={<BillingOperationsPage />} />
          <Route path="billing/commerce" element={<BillingCommercePage />} />
          <Route path="billing/subscriptions" element={<BillingSubscriptionsPage />} />
          <Route path="billing/packs" element={<BillingPacksPage />} />
          <Route path="billing/orders" element={<BillingOrdersPage />} />
          <Route path="billing/consumption" element={<BillingUserConsumptionPage />} />
          <Route path="billing/ledger" element={<BillingLedgerPage />} />
          <Route path="access" element={<AccessPage />} />
          <Route path="access/eligibility" element={<Navigate to="/access" replace />} />
          <Route path="trading-config" element={<Navigate to="/access" replace />} />
          <Route path="observability/runtime-health" element={<Navigate to="/observability" replace />} />
          <Route path="observability/alerts" element={<Navigate to="/observability" replace />} />
          <Route path="observability" element={<ObservabilityPage />} />
          <Route path="integrations/telegram" element={<Navigate to="/system/channels/telegram" replace />} />
          <Route path="integrations/exchange-apis" element={<Navigate to="/system/channels" replace />} />
          <Route path="integrations/llm-providers" element={<Navigate to="/ai-settings" replace />} />
          <Route path="integrations" element={<Navigate to="/system/channels" replace />} />
          <Route path="system/channels/:channelId" element={<ChannelConfigPage />} />
          <Route path="system/channels" element={<ChannelConfigPage />} />
          <Route path="system/feature-flags" element={<Navigate to="/runtime/executions" replace />} />
          <Route path="system/contract-closure" element={<Navigate to="/runtime/executions" replace />} />
          <Route path="system/global-gate" element={<Navigate to="/runtime/executions" replace />} />
          </Route>
        </Routes>
      </ConfirmationRulesProvider>
    </OrchestrationPolicyProvider>
  );
}
