type RuntimePublicConfig = {
  apiBase?: string;
  useMock?: string | boolean;
  apiTimeout?: number | string;
  apiMaxRetries?: number | string;
  apiRetryBaseDelay?: number | string;
  apiRetryMaxDelay?: number | string;
};

declare global {
  interface Window {
    __DREAMTEAMS_CONFIG__?: RuntimePublicConfig;
  }
}

const asString = (value: unknown, fallback: string): string => {
  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }

  return fallback;
};

const asNumber = (value: unknown, fallback: number): number => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return fallback;
};

export const useRuntimePublicConfig = () => {
  const config = useRuntimeConfig();
  const runtimeConfig = import.meta.client
    ? window.__DREAMTEAMS_CONFIG__
    : undefined;

  return {
    apiBase: asString(runtimeConfig?.apiBase, config.public.apiBase as string),
    useMock: asString(runtimeConfig?.useMock, config.public.useMock as string),
    apiTimeout: asNumber(
      runtimeConfig?.apiTimeout,
      config.public.apiTimeout as number,
    ),
    apiMaxRetries: asNumber(
      runtimeConfig?.apiMaxRetries,
      config.public.apiMaxRetries as number,
    ),
    apiRetryBaseDelay: asNumber(
      runtimeConfig?.apiRetryBaseDelay,
      config.public.apiRetryBaseDelay as number,
    ),
    apiRetryMaxDelay: asNumber(
      runtimeConfig?.apiRetryMaxDelay,
      config.public.apiRetryMaxDelay as number,
    ),
  };
};
