// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },

  modules: ["@nuxt/ui", "@pinia/nuxt", "@nuxtjs/i18n"],

  css: ["~/assets/css/main.css"],

  typescript: {
    strict: true,
    typeCheck: true,
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost",
      useMock: process.env.NUXT_PUBLIC_USE_MOCK || "false",
    },
  },

  nitro: {
    prerender: {
      routes: ['/'],
      ignore: ['/me', '/onboarding', '/start'],
      crawlLinks: true,
      failOnError: false,
    },
  },

  // Enable SPA mode for proper 404 handling with static generation
  ssr: false,

  // i18n configuration
  i18n: {
    locales: [
      {
        code: "ru",
        language: "ru-RU",
        file: "ru.json",
        name: "Русский",
      },
      {
        code: "en",
        language: "en-US",
        file: "en.json",
        name: "English",
      },
    ],
    defaultLocale: "ru",
    langDir: "../locales", // Relative to app directory
    strategy: "no_prefix", // Language stored in cookie only, no URL prefix
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: "i18n_locale",
      redirectOn: "root",
      alwaysRedirect: false,
    },
    vueI18n: "./i18n.config.ts", // Path to i18n config file
  },
});
