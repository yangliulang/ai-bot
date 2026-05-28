import { Navigate, Route, Routes } from "react-router-dom";
import StandalonePageShell from "@/layout/StandalonePageShell";
import WebShell from "@/layout/WebShell";
import HomePage from "@/pages/HomePage";
import AgentOnboardingPage from "@/pages/onboarding/AgentOnboardingPage";
import BillingSummaryStubPage from "@/pages/billing/BillingSummaryStubPage";
import AgentBillingPage from "@/pages/subaccount/AgentBillingPage";
import BillingPage from "@/pages/subaccount/BillingPage";
import MySubscriptionPage from "@/pages/subscription/MySubscriptionPage";
import SubscriptionCheckoutPage from "@/pages/subscription/SubscriptionCheckoutPage";
import SubscriptionPackPage from "@/pages/subscription/SubscriptionPackPage";
import SubscriptionUpgradePage from "@/pages/subscription/SubscriptionUpgradePage";
import H5PlaceholderPage from "@/pages/h5/H5PlaceholderPage";

const redirectOnboarding = <Navigate to="/onboarding" replace />;

export default function App() {
  return (
    <Routes>
      <Route
        path="/onboarding"
        element={
          <StandalonePageShell>
            <AgentOnboardingPage />
          </StandalonePageShell>
        }
      />
      <Route path="/onboarding/subaccount-api" element={redirectOnboarding} />
      <Route path="/onboarding/telegram-binding" element={redirectOnboarding} />
      <Route path="/onboarding/instance-ready" element={redirectOnboarding} />

      <Route element={<WebShell />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/billing/summary" element={<BillingSummaryStubPage />} />
        <Route path="/subaccount/billing" element={<BillingPage />} />
        <Route path="/subaccount/agent-billing" element={<AgentBillingPage />} />
        <Route path="/subscription" element={<MySubscriptionPage />} />
        <Route path="/subscription/upgrade" element={<SubscriptionUpgradePage />} />
        <Route path="/subscription/pack" element={<SubscriptionPackPage />} />
        <Route path="/subscription/checkout" element={<SubscriptionCheckoutPage />} />
        <Route path="/commerce/upgrade" element={<Navigate to="/subscription/upgrade" replace />} />
        <Route path="/commerce/pack" element={<Navigate to="/subscription/pack" replace />} />
        <Route path="/h5/market" element={<H5PlaceholderPage title="行情" />} />
        <Route path="/h5/futures" element={<H5PlaceholderPage title="合约" />} />
      </Route>
    </Routes>
  );
}
