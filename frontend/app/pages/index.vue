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
    <HomeHeroSection :stats="stats" @start="handleStart" />

    <!-- About Section -->
    <HomeAboutSection />

    <!-- Features Section -->
    <HomeFeaturesSection :features="features" />

    <!-- Why We're the Best Section -->
    <HomeWhyBestSection :items="whyBest" />

    <!-- Call to Action Section -->
    <HomeCtaSection @start="handleStart" />
  </div>
</template>
