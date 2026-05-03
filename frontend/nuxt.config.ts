// https://nuxt.com/docs/api/configuration/nuxt-config
const seoDescription = "DreamTeams - IT hackathon aggregator and team search platform.";

export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: {
    enabled: true,

    timeline: {
      enabled: true,
    },
  },

  modules: ["@nuxt/ui", "@pinia/nuxt", "@nuxtjs/i18n"],

  css: ["~/assets/css/main.css"],

  app: {
    head: {
      title: "DreamTeams",
      titleTemplate: "DreamTeams",
      htmlAttrs: {
        lang: "ru",
      },
      script: [{ src: "/config.js", defer: false }],
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        { name: "theme-color", content: "#3b82f6" },
        { name: "description", content: seoDescription },
        { name: "robots", content: "index, follow" },
        { property: "og:type", content: "website" },
        { property: "og:site_name", content: "DreamTeams" },
        { property: "og:title", content: "DreamTeams" },
        { property: "og:description", content: seoDescription },
        { property: "og:image", content: "/banner.webp" },
        { property: "og:image:type", content: "image/webp" },
        { property: "og:image:width", content: "1536" },
        { property: "og:image:height", content: "1024" },
        { name: "twitter:card", content: "summary_large_image" },
        { name: "twitter:title", content: "DreamTeams" },
        { name: "twitter:description", content: seoDescription },
        { name: "twitter:image", content: "/banner.webp" },
      ],
      link: [
        { rel: "icon", type: "image/x-icon", href: "/favicon.ico" },
        { rel: "icon", type: "image/png", sizes: "32x32", href: "/favicon-32x32.png" },
        { rel: "icon", type: "image/png", sizes: "16x16", href: "/favicon-16x16.png" },
        { rel: "apple-touch-icon", sizes: "180x180", href: "/apple-touch-icon.png" },
        { rel: "manifest", href: "/site.webmanifest" },
      ],
    },
  },

  typescript: {
    strict: true,
    typeCheck: true,
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost",
      useMock: process.env.NUXT_PUBLIC_USE_MOCK || "false",
      // Request timeout in milliseconds
      apiTimeout: Number(process.env.NUXT_PUBLIC_API_TIMEOUT) || 10000,
      // Maximum number of retry attempts after a failed request
      apiMaxRetries: Number(process.env.NUXT_PUBLIC_API_MAX_RETRIES) || 3,
      // Base delay in ms for exponential backoff (delay = baseDelay * 2^attempt + jitter)
      apiRetryBaseDelay: Number(process.env.NUXT_PUBLIC_API_RETRY_BASE_DELAY) || 300,
      // Upper bound on retry delay in ms
      apiRetryMaxDelay: Number(process.env.NUXT_PUBLIC_API_RETRY_MAX_DELAY) || 10000,
    },
  },

  ...({
    nitro: {
    prerender: {
      routes: ['/'],
      ignore: ['/me', '/onboarding', '/start'],
      crawlLinks: true,
      failOnError: false,
    },
    },
  } as Record<string, unknown>),

  vite: {
    server: {
      hmr:
        process.env.NUXT_DEV_PROXY === "1"
          ? {
              clientPort: 80,
            }
          : undefined,
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
