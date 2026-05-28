import { Button } from "antd";
import type { ButtonProps } from "antd/es/button";
import { forwardRef } from "react";
import { ADMIN_FILTER_CONTROL_SIZE } from "./presets";

/** 页头 / 筛选条主干操作：统一 middle 档位，避免散落 large/default */
export const PagePrimaryButton = forwardRef<HTMLAnchorElement | HTMLButtonElement, Omit<ButtonProps, "type" | "size">>(
  (props, ref) => <Button ref={ref} type="primary" size={ADMIN_FILTER_CONTROL_SIZE} {...props} />,
);

PagePrimaryButton.displayName = "PagePrimaryButton";

/** 次级操作按钮（重置、清空、骨架一致） */
export const PageSecondaryButton = forwardRef<HTMLAnchorElement | HTMLButtonElement, Omit<ButtonProps, "type" | "size">>(
  (props, ref) => <Button ref={ref} type="default" size={ADMIN_FILTER_CONTROL_SIZE} {...props} />,
);

PageSecondaryButton.displayName = "PageSecondaryButton";
