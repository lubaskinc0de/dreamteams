export default defineAppConfig({
  ui: {
    primary: "blue",
    gray: "slate",

    // Page components configuration
    pageHeader: {
      slots: {
        wrapper: "flex flex-col gap-4",
      },
    },

    formField: {
      slots: {
        label: "block font-medium text-default mb-2",
      },
    },

    // Toast/Notification configuration
    notifications: {
      position: "top-0 right-0",
    },

    // Custom animation classes for reuse
    animations: {
      cardHover:
        "hover:shadow-xl transition-all duration-300 hover:-translate-y-1",
      iconSpin: "animate-spin",
      fadeIn: "transition-opacity duration-300",
      slideIn: "transition-transform duration-300",
    },

    // Custom spacing utilities
    spacing: {
      cardGap: "gap-6",
      sectionMargin: "mt-16",
      containerPadding: "px-4 sm:px-6 lg:px-8",
    },

    // Semantic color tokens for theming
    semantic: {
      background: {
        primary: "bg-gray-900",
        secondary: "bg-gray-800",
        elevated: "bg-gray-700",
        card: "bg-gray-800/90",
      },
      text: {
        primary: "text-gray-100",
        secondary: "text-gray-400",
        muted: "text-gray-500",
        highlighted: "text-primary-400",
      },
      border: {
        default: "border-gray-700",
        subtle: "border-gray-700/50",
      },
    },

    // Icon configuration
    icons: {
      close: "i-heroicons-x-mark-20-solid",
      check: "i-heroicons-check-circle",
      error: "i-heroicons-exclamation-circle",
      warning: "i-heroicons-exclamation-triangle",
      info: "i-heroicons-information-circle",
      loading: "i-heroicons-arrow-path",
    },
  },

  // Color mode configuration
  colorMode: {
    preference: "system",
    fallback: "light",
    classSuffix: "",
  },
});
