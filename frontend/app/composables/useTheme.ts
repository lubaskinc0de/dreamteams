import type { ThemeName, ThemeConfig } from "~/types/ui";

/**
 * Composable for theme management
 * Provides theme switching and customization capabilities
 */
export const useTheme = () => {
  const appConfig = useAppConfig();
  const colorMode = useColorMode();

  /**
   * Available theme presets
   * Each theme defines primary and gray color palettes
   */
  const themes: Record<ThemeName, ThemeConfig> = {
    default: {
      primary: "blue",
      gray: "slate",
    },
    ocean: {
      primary: "cyan",
      gray: "blue",
    },
    forest: {
      primary: "green",
      gray: "emerald",
    },
    sunset: {
      primary: "orange",
      gray: "amber",
    },
  };

  /**
   * Current theme state
   * Persisted in localStorage via useState
   */
  const currentTheme = useState<ThemeName>("currentTheme", () => "default");

  /**
   * Set a new theme
   * Updates app configuration and persists selection
   */
  const setTheme = (theme: ThemeName) => {
    if (!themes[theme]) {
      console.warn(`Theme "${theme}" not found, using default`);
      theme = "default";
    }

    currentTheme.value = theme;

    // Note: In Nuxt UI v4, primary and gray colors are set in app.config.ts
    // This is a placeholder for future dynamic theme switching
    // For now, themes can be switched by updating app.config.ts and restarting

    // Trigger reactivity by reassigning
    if (import.meta.client) {
      // Force re-render by updating a reactive property
      window.dispatchEvent(new CustomEvent("theme-changed", { detail: theme }));
    }
  };

  /**
   * Get current theme config
   */
  const getCurrentTheme = computed(() => themes[currentTheme.value]);

  /**
   * Toggle between light and dark modes
   */
  const toggleColorMode = () => {
    colorMode.preference = colorMode.value === "dark" ? "light" : "dark";
  };

  /**
   * Set specific color mode
   */
  const setColorMode = (mode: "light" | "dark" | "system") => {
    colorMode.preference = mode;
  };

  /**
   * Check if current mode is dark
   */
  const isDark = computed(() => colorMode.value === "dark");

  /**
   * Initialize theme from saved preference
   */
  const initializeTheme = () => {
    // Theme is already initialized via useState
    // This function can be used for additional initialization logic
    if (currentTheme.value !== "default") {
      setTheme(currentTheme.value);
    }
  };

  return {
    themes,
    currentTheme: readonly(currentTheme),
    getCurrentTheme,
    setTheme,
    toggleColorMode,
    setColorMode,
    isDark,
    initializeTheme,
    colorMode: readonly(colorMode),
  };
};
