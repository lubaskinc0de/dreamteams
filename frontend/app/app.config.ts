export default defineAppConfig({
  ui: {
    colors: {
      primary: "lavender",
      neutral: "neutral",
    },

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

    // Tooltip: override the default single-line truncated bubble to allow
    // wrapped multi-line help text with comfortable padding and radius.
    tooltip: {
      slots: {
        content:
          "flex items-start gap-1 bg-default text-default shadow-md rounded-lg ring ring-default max-w-xs px-3 py-2 text-sm leading-snug select-none data-[state=delayed-open]:animate-[scale-in_100ms_ease-out] data-[state=closed]:animate-[scale-out_100ms_ease-in] origin-(--reka-tooltip-content-transform-origin) pointer-events-auto",
        arrow: "fill-bg stroke-default",
        text: "whitespace-normal text-wrap",
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
