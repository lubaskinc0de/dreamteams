/**
 * Vue I18n configuration
 * Provides additional configuration for the i18n plugin
 */
export default defineI18nConfig(() => ({
  legacy: false,
  locale: "ru",
  fallbackLocale: "ru",
  messages: {},
  numberFormats: {
    ru: {
      currency: {
        style: "currency",
        currency: "RUB",
        notation: "standard",
      },
      decimal: {
        style: "decimal",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      },
      percent: {
        style: "percent",
        useGrouping: false,
      },
    },
    en: {
      currency: {
        style: "currency",
        currency: "USD",
        notation: "standard",
      },
      decimal: {
        style: "decimal",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      },
      percent: {
        style: "percent",
        useGrouping: false,
      },
    },
  },
  datetimeFormats: {
    ru: {
      short: {
        year: "numeric",
        month: "short",
        day: "numeric",
      },
      long: {
        year: "numeric",
        month: "long",
        day: "numeric",
        weekday: "long",
        hour: "numeric",
        minute: "numeric",
      },
    },
    en: {
      short: {
        year: "numeric",
        month: "short",
        day: "numeric",
      },
      long: {
        year: "numeric",
        month: "long",
        day: "numeric",
        weekday: "long",
        hour: "numeric",
        minute: "numeric",
      },
    },
  },
}));
