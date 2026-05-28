import { useCallback, useEffect, useMemo, useState } from "react";
import { COMMERCE_RECEIVE_ADDRESSES } from "@/data/commercePaymentAddresses";
import { findPack, findPlan } from "@/data/subscriptionCatalogMock";
import { createDemoCommerceOrderId } from "@/lib/commerceOrderId";

export type CheckoutKind = "upgrade" | "pack";

export type CryptoNetworkId = "USDT_TRC20" | "USDT_ERC20" | "BTC";

const NETWORKS: { id: CryptoNetworkId; label: string; confirmBlocks: number }[] = [
  { id: "USDT_TRC20", label: "USDT · TRON (TRC20)", confirmBlocks: 19 },
  { id: "USDT_ERC20", label: "USDT · Ethereum (ERC20)", confirmBlocks: 12 },
  { id: "BTC", label: "BTC · Bitcoin", confirmBlocks: 2 },
];

export type CryptoCheckoutStep = "review" | "transfer" | "confirming" | "success" | "expired";

export function useCryptoCheckout(kind: CheckoutKind, sku: string) {
  const product = useMemo(() => {
    if (kind === "upgrade") return findPlan(sku);
    return findPack(sku);
  }, [kind, sku]);

  const amountUsdt = product?.priceUsdt ?? "0";

  const title = product
    ? "tagline" in product
      ? `${product.name} · ${product.tagline}`
      : product.name
    : "未知商品";

  const [step, setStep] = useState<CryptoCheckoutStep>("review");
  const [network, setNetwork] = useState<CryptoNetworkId>("USDT_TRC20");
  const [orderId] = useState(() => createDemoCommerceOrderId());
  const [secondsLeft, setSecondsLeft] = useState(30 * 60);
  const [confirmProgress, setConfirmProgress] = useState(0);

  const depositAddress = COMMERCE_RECEIVE_ADDRESSES[network];
  const networkMeta = NETWORKS.find((n) => n.id === network)!;

  useEffect(() => {
    if (step !== "transfer") return;
    if (secondsLeft <= 0) {
      setStep("expired");
      return;
    }
    const t = window.setInterval(() => setSecondsLeft((s) => s - 1), 1000);
    return () => window.clearInterval(t);
  }, [step, secondsLeft]);

  useEffect(() => {
    if (step !== "confirming") return;
    setConfirmProgress(0);
    let n = 0;
    const target = networkMeta.confirmBlocks;
    const t = window.setInterval(() => {
      n += 1;
      setConfirmProgress(n);
      if (n >= target) {
        window.clearInterval(t);
        setStep("success");
      }
    }, 800);
    return () => window.clearInterval(t);
  }, [step, networkMeta.confirmBlocks]);

  const startTransfer = useCallback(() => {
    setSecondsLeft(30 * 60);
    setStep("transfer");
  }, []);

  const markPaidDemo = useCallback(() => {
    setStep("confirming");
  }, []);

  const reset = useCallback(() => {
    setStep("review");
    setSecondsLeft(30 * 60);
    setConfirmProgress(0);
  }, []);

  return {
    product,
    title,
    amountUsdt,
    kind,
    sku,
    step,
    setStep,
    network,
    setNetwork,
    networks: NETWORKS,
    orderId,
    depositAddress,
    networkMeta,
    secondsLeft,
    confirmProgress,
    startTransfer,
    markPaidDemo,
    reset,
  };
}
