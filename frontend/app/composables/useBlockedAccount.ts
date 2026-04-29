import type { ApiError } from "~/types/api";

export interface BlockedAccountMeta {
  reason: string | null;
  blocked_at: string | null;
  account_id: string | null;
  [key: string]: unknown;
}

const readString = (value: unknown): string | null =>
  typeof value === "string" && value.trim().length > 0 ? value : null;

export const useBlockedAccount = () => {
  const isAccountBlocked = useState<boolean>("auth-isAccountBlocked", () => false);
  const blockedAccount = useState<BlockedAccountMeta | null>(
    "auth-blockedAccount",
    () => null,
  );

  const accountBlockedError = computed<ApiError>(() => ({
    code: "ACCOUNT_BLOCKED",
    message: "Your account has been blocked",
    meta: blockedAccount.value,
  }));

  const blockFromError = (error: ApiError) => {
    if (error.code !== "ACCOUNT_BLOCKED") {
      return;
    }

    const meta = error.meta ?? {};
    blockedAccount.value = {
      ...meta,
      reason: readString(meta.reason),
      blocked_at: readString(meta.blocked_at),
      account_id:
        readString(meta.account_id) ??
        readString(meta.user_id) ??
        readString(meta.auth_user_id),
    };
    isAccountBlocked.value = true;
  };

  const clearBlockedAccount = () => {
    isAccountBlocked.value = false;
    blockedAccount.value = null;
  };

  return {
    isAccountBlocked,
    blockedAccount,
    accountBlockedError,
    blockFromError,
    clearBlockedAccount,
  };
};
