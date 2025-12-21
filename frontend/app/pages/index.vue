<script setup lang="ts">
import type { Feature, Stat } from "~/types/ui";

// Get navigation links from composable
const { heroLinks } = useNavigation();

// Get i18n
const { t } = useI18n();

// SEO Meta tags
useSeoMeta({
  title: t("seo.home.title"),
  description: t("seo.home.description"),
  ogTitle: t("seo.home.title"),
  ogDescription: t("seo.home.description"),
  ogImage: "/og-image.png",
  twitterCard: "summary_large_image",
});

// Features with type safety and i18n
const features: Feature[] = [
  {
    icon: "i-heroicons-rectangle-stack",
    title: t("home.features.aggregator.title"),
    description: t("home.features.aggregator.description"),
    badge: {
      label: t("home.features.aggregator.badge"),
      color: "success" as const,
    },
  },
  {
    icon: "i-heroicons-user-group",
    title: t("home.features.teams.title"),
    description: t("home.features.teams.description"),
    badge: { label: t("home.features.teams.badge"), color: "info" as const },
  },
  {
    icon: "i-heroicons-chart-bar",
    title: t("home.features.organizers.title"),
    description: t("home.features.organizers.description"),
    badge: {
      label: t("home.features.organizers.badge"),
      color: "warning" as const,
    },
  },
];

// Stats with type safety and i18n
const stats: Stat[] = [
  {
    icon: "i-heroicons-trophy",
    value: t("home.stats.hackathons.value"),
    label: t("home.stats.hackathons.label"),
    color: "text-success-400",
  },
  {
    icon: "i-heroicons-user-group",
    value: t("home.stats.teams.value"),
    label: t("home.stats.teams.label"),
    color: "text-info-400",
  },
  {
    icon: "i-heroicons-users",
    value: t("home.stats.participants.value"),
    label: t("home.stats.participants.label"),
    color: "text-warning-400",
  },
];
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
    <!-- Hero Section with Gradient Background -->
    <section class="relative overflow-hidden py-16 sm:py-20">
      <!-- Background Decoration -->
      <div class="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-success-500/5 dark:from-primary-500/10 dark:to-success-500/10"></div>
      <div class="absolute top-0 right-0 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 left-0 w-96 h-96 bg-success-500/10 rounded-full blur-3xl"></div>

      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-4xl mx-auto">
          <!-- Main Title -->
          <h1 class="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-gray-900 dark:text-white mb-6 animate-fade-in">
            <span class="bg-gradient-to-r from-primary-600 to-success-600 dark:from-primary-400 dark:to-success-400 bg-clip-text text-transparent">
              {{ t('home.title') }}
            </span>
          </h1>

          <!-- Subtitle -->
          <p class="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
            {{ t('home.description') }}
          </p>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <UButton
              v-for="(link, index) in heroLinks"
              :key="index"
              :variant="link.variant || 'solid'"
              :size="link.size"
              :icon="link.icon"
              @click="() => link.click()"
              color="primary"
              class="shadow-lg hover:shadow-xl transition-all"
            >
              {{ link.label }}
            </UButton>
          </div>

          <!-- Stats Cards - Compact -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto">
            <div
              v-for="(stat, index) in stats"
              :key="index"
              class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1"
            >
              <div class="flex items-center justify-center gap-3 mb-2">
                <UIcon :name="stat.icon" :class="['text-2xl', stat.color]" />
                <span class="text-3xl font-bold text-gray-900 dark:text-gray-100">
                  {{ stat.value }}
                </span>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ stat.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-12 relative">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-10">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-3">
            {{ t('home.featuresTitle') }}
          </h2>
          <p class="text-lg text-gray-600 dark:text-gray-400">
            {{ t('home.featuresDescription') }}
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            v-for="(feature, index) in features"
            :key="index"
            class="group relative bg-white dark:bg-gray-800 rounded-2xl p-8 border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2"
          >
            <!-- Icon with gradient background -->
            <div class="mb-5 inline-flex p-4 rounded-xl bg-gradient-to-br from-primary-500/10 to-success-500/10 group-hover:from-primary-500/20 group-hover:to-success-500/20 transition-colors">
              <UIcon :name="feature.icon" class="text-4xl text-primary-600 dark:text-primary-400" />
            </div>

            <!-- Title -->
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-3">
              {{ feature.title }}
            </h3>

            <!-- Description -->
            <p class="text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
              {{ feature.description }}
            </p>

            <!-- Badge -->
            <UBadge
              :label="feature.badge.label"
              :color="feature.badge.color"
              variant="subtle"
              size="sm"
              class="inline-flex"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- Call to Action Section -->
    <section class="py-16 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-primary-600/10 via-success-600/10 to-primary-600/10 dark:from-primary-600/20 dark:via-success-600/20 dark:to-primary-600/20"></div>

      <div class="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Готовы начать?
        </h2>
        <p class="text-lg text-gray-600 dark:text-gray-300 mb-8">
          Присоединяйтесь к растущему сообществу организаторов и участников хакатонов
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <UButton
            to="/register"
            color="primary"
            size="xl"
            icon="i-heroicons-rocket-launch"
            class="shadow-lg hover:shadow-xl transition-all"
          >
            {{ t('home.registerButton') }}
          </UButton>
        </div>
      </div>
    </section>
  </div>
</template>
