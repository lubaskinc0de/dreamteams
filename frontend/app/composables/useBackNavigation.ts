interface BackNavigationOptions {
  fallback?: string | (() => string);
}

const resolveFallback = (fallback: string | (() => string)) =>
  typeof fallback === "function" ? fallback() : fallback;

export const useBackNavigation = (defaultFallback = "/") => {
  const router = useRouter();

  const navigateBack = (options: BackNavigationOptions = {}) => {
    const fallback = options.fallback ?? defaultFallback;

    if (import.meta.client && window.history.state?.back) {
      router.back();
      return;
    }

    router.push(resolveFallback(fallback));
  };

  return {
    navigateBack,
  };
};
