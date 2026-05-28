import type { CryptoNetworkId } from "@/hooks/useCryptoCheckout";

/** 同窗 `src/admin/src/data/commercePaymentAddresses.ts` */
export const COMMERCE_RECEIVE_ADDRESSES: Record<CryptoNetworkId, string> = {
  USDT_TRC20: "TXyz9demoTronUsdtReceiveAddress0001",
  USDT_ERC20: "0xDemoErc20UsdtReceive0000000000000001",
  BTC: "bc1qdemoBTCreceive000000000000000",
};
