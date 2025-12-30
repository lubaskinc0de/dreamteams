<script setup lang="ts">
import type { Feature, Stat } from "~/types/ui";

// Get i18n
const { t } = useI18n();

// Auth composable
const { login } = useAuth();

// Start button handler
const handleStart = async () => {
  await login();
};

// Scroll animations - only for landing page
onMounted(() => {
  if (!import.meta.client) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
        }
      });
    },
    {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px',
    }
  );

  // Observe all elements with animation classes
  const animatedElements = document.querySelectorAll(
    '.fade-in-scroll, .fade-in-left, .fade-in-right, .scale-in-scroll, .stagger-children'
  );

  animatedElements.forEach((el) => {
    observer.observe(el);
  });

  // Cleanup on unmount
  onUnmounted(() => {
    observer.disconnect();
  });
});

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
    value: t("home.stats.competitions.value"),
    label: t("home.stats.competitions.label"),
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

// Why we're the best
const whyBest = [
  {
    icon: "i-heroicons-star",
    title: t("home.whyBest.unique.title"),
    description: t("home.whyBest.unique.description"),
  },
  {
    icon: "i-heroicons-chart-bar-square",
    title: t("home.whyBest.demand.title"),
    description: t("home.whyBest.demand.description"),
  },
  {
    icon: "i-heroicons-shield-check",
    title: t("home.whyBest.transparent.title"),
    description: t("home.whyBest.transparent.description"),
  },
  {
    icon: "i-heroicons-trophy",
    title: t("home.whyBest.rating.title"),
    description: t("home.whyBest.rating.description"),
  },
];
</script>

<template>
  <div>
    <!-- Hero Section -->
    <section class="relative overflow-hidden py-16 sm:py-24 lg:py-32 bg-gradient-to-br from-primary-500/10 via-success-500/5 to-primary-500/10 dark:from-primary-500/20 dark:via-success-500/10 dark:to-primary-500/20">
      <!-- Background Decoration -->
      <div class="absolute top-0 right-0 w-72 h-72 sm:w-96 sm:h-96 bg-primary-500/20 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-0 left-0 w-72 h-72 sm:w-96 sm:h-96 bg-success-500/20 rounded-full blur-3xl animate-pulse [animation-delay:1000ms]"></div>

      <UContainer>
        <div class="text-center max-w-4xl mx-auto">
          <!-- Brand Name -->
          <h1 class="text-6xl sm:text-7xl md:text-8xl lg:text-9xl font-extrabold mb-4 sm:mb-6 scale-in-scroll">
            <span class="bg-gradient-to-r from-primary-600 to-success-600 dark:from-primary-400 dark:to-success-400 bg-clip-text text-transparent">
              {{ t('home.title') }}
            </span>
          </h1>

          <!-- Slogan -->
          <p class="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-6 sm:mb-8 fade-in-scroll">
            {{ t('home.heroTitle') }}
          </p>

          <!-- CTA Text -->
          <p class="text-base sm:text-lg md:text-xl font-semibold text-primary-600 dark:text-primary-400 mb-8 sm:mb-10 max-w-2xl mx-auto px-4 fade-in-scroll">
            {{ t('home.ctaText') }}
          </p>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12 sm:mb-16 fade-in-scroll">
            <UButton
              @click="handleStart"
              size="xl"
              icon="i-heroicons-rocket-launch"
              color="primary"
              variant="solid"
              class="!px-8 !py-4 !text-lg sm:!text-xl"
            >
              {{ t('home.startButton') }}
            </UButton>
          </div>

          <!-- Stats Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 max-w-4xl mx-auto px-4 stagger-children">
            <UCard
              v-for="(stat, index) in stats"
              :key="index"
              variant="soft"
              class="card-hover-smooth"
            >
              <div class="flex items-center justify-center gap-2 sm:gap-3 mb-2">
                <UIcon :name="stat.icon" :class="['text-2xl sm:text-3xl', stat.color]" />
                <span class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-gray-100">
                  {{ stat.value }}
                </span>
              </div>
              <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 text-center">{{ stat.label }}</p>
            </UCard>
          </div>
        </div>
      </UContainer>
    </section>

    <!-- About Section -->
    <section class="py-16 sm:py-20 bg-white dark:bg-gray-900">
      <UContainer>
        <div class="max-w-3xl mx-auto text-center px-4 fade-in-scroll">
          <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4 sm:mb-6 fade-in-left">
            {{ t('home.about.title') }}
          </h2>
          <p class="text-base sm:text-lg text-gray-600 dark:text-gray-400 leading-relaxed fade-in-right">
            {{ t('home.about.description') }}
          </p>
        </div>
      </UContainer>
    </section>

    <!-- Features Section -->
    <section class="py-16 sm:py-20 bg-gray-50 dark:bg-gray-800/50">
      <UContainer>
        <div class="text-center mb-12 sm:mb-16 px-4 fade-in-scroll">
          <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
            {{ t('home.featuresTitle') }}
          </h2>
          <p class="text-base sm:text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            {{ t('home.featuresDescription') }}
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 px-4 stagger-children">
          <UCard
            v-for="(feature, index) in features"
            :key="index"
            variant="outline"
            class="flex flex-col card-hover-smooth"
          >
            <template #header>
              <div class="flex items-center gap-3 sm:gap-4">
                <div class="p-2 sm:p-3 rounded-xl bg-gradient-to-br from-primary-500/10 to-success-500/10">
                  <UIcon :name="feature.icon" class="text-2xl sm:text-3xl text-primary-600 dark:text-primary-400" />
                </div>
                <h3 class="text-base sm:text-lg md:text-xl font-semibold text-gray-900 dark:text-white">
                  {{ feature.title }}
                </h3>
              </div>
            </template>

            <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400 leading-relaxed flex-grow break-words">
              {{ feature.description }}
            </p>

            <template #footer>
              <UBadge
                :label="feature.badge.label"
                :color="feature.badge.color"
                variant="subtle"
                size="sm"
              />
            </template>
          </UCard>
        </div>
      </UContainer>
    </section>

    <!-- Why We're the Best Section -->
    <section class="py-16 sm:py-20 bg-white dark:bg-gray-900">
      <UContainer>
        <div class="text-center mb-12 sm:mb-16 px-4 fade-in-scroll">
          <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {{ t('home.whyBest.title') }}
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 max-w-5xl mx-auto px-4 stagger-children">
          <UCard
            v-for="(item, index) in whyBest"
            :key="index"
            variant="soft"
            class="card-hover-smooth"
          >
            <div class="flex items-start gap-3 sm:gap-4">
              <div class="p-2 sm:p-3 rounded-xl bg-gradient-to-br from-primary-500/20 to-success-500/20 flex-shrink-0">
                <UIcon :name="item.icon" class="text-2xl sm:text-3xl text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-2 break-words">
                  {{ item.title }}
                </h3>
                <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400 leading-relaxed break-words">
                  {{ item.description }}
                </p>
              </div>
            </div>
          </UCard>
        </div>
      </UContainer>
    </section>

    <!-- Call to Action Section -->
    <section class="py-16 sm:py-20 relative overflow-hidden bg-gradient-to-r from-primary-600/10 via-success-600/10 to-primary-600/10 dark:from-primary-600/20 dark:via-success-600/20 dark:to-primary-600/20">
      <UContainer>
        <div class="text-center max-w-3xl mx-auto px-4 scale-in-scroll">
          <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
            {{ t('home.cta.title') }}
          </h2>
          <p class="text-base sm:text-lg text-gray-600 dark:text-gray-300 mb-6 sm:mb-8">
            {{ t('home.cta.description') }}
          </p>
          <UButton
            @click="handleStart"
            color="primary"
            size="xl"
            icon="i-heroicons-rocket-launch"
            class="!px-8 !py-4 !text-lg sm:!text-xl"
          >
            {{ t('home.startButton') }}
          </UButton>
        </div>
      </UContainer>
    </section>
  </div>
</template>
