import type { MockCommerceCryptoPaymentNetwork } from "./types";

/** 同窗 `src/Web` · `useCryptoCheckout` DEMO_ADDRESSES */
export const COMMERCE_RECEIVE_ADDRESSES: Record<MockCommerceCryptoPaymentNetwork, string> = {
  USDT_TRC20: "TXyz9demoTronUsdtReceiveAddress0001",
  USDT_ERC20: "0xDemoErc20UsdtReceive0000000000000001",
};

export function receiveAddressForNetwork(network: MockCommerceCryptoPaymentNetwork): string {
  return COMMERCE_RECEIVE_ADDRESSES[network];
}
