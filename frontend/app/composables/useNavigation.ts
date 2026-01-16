/**
 * Composable for centralized navigation configuration
 * Provides consistent navigation links and actions across the application
 */
export const useNavigation = () => {
  const router = useRouter();
  const { t } = useI18n();

  /**
   * Main navigation links for header/layout
   */
  const mainLinks = computed(() => [
    {
      label: t("nav.home"),
      icon: "i-heroicons-home",
      to: "/",
    },
    {
      label: t("nav.profile"),
      icon: "i-heroicons-user",
      to: "/me",
    },
    {
      label: t("nav.register"),
      icon: "i-heroicons-user-plus",
      to: "/onboarding",
    },
  ]);

  /**
   * Hero section action links for landing page
   */
  const heroLinks = computed(() => [
    {
      label: t("home.startButton"),
      icon: "i-heroicons-rocket-launch",
      size: "xl" as const,
      click: async () => {
        const { login } = useAuth();
        await login();
      },
    },
  ]);

  /**
   * Footer navigation links
   */
  const footerLinks = computed(() => [
    {
      label: t("footer.support"),
      icon: "i-heroicons-envelope",
      to: "mailto:support@posutochnik.ru",
    },
    {
      label: t("footer.documentation"),
      icon: "i-heroicons-document-text",
      to: "#", // TODO: Add documentation link when available
    },
  ]);

  /**
   * Navigate to a specific route
   */
  const navigateTo = (path: string) => {
    return router.push(path);
  };

  /**
   * Navigate back
   */
  const navigateBack = () => {
    return router.back();
  };

  return {
    mainLinks,
    heroLinks,
    footerLinks,
    navigateTo,
    navigateBack,
  };
};
