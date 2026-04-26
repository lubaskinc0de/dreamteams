<script setup lang="ts">
import type { Feature } from "~/types/ui";

// Get i18n
const { t } = useI18n();

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

const organizerFeatures: Feature[] = [
  {
    icon: "i-heroicons-building-office-2",
    title: t("home.features.organizers.title"),
    description: t("home.features.organizers.description"),
    badge: {
      label: t("home.features.organizers.badge"),
      color: "warning" as const,
    },
  },
  {
    icon: "i-heroicons-document-text",
    title: t("home.features.forms.title"),
    description: t("home.features.forms.description"),
    badge: {
      label: t("home.features.forms.badge"),
      color: "neutral" as const,
    },
  },
  {
    icon: "i-heroicons-document-arrow-down",
    title: t("home.features.applications.title"),
    description: t("home.features.applications.description"),
    badge: {
      label: t("home.features.applications.badge"),
      color: "primary" as const,
    },
  },
];

const participantFeatures: Feature[] = [
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
    icon: "i-heroicons-user-circle",
    title: t("home.features.participants.title"),
    description: t("home.features.participants.description"),
    badge: { label: t("home.features.participants.badge"), color: "info" as const },
  },
  {
    icon: "i-heroicons-paper-airplane",
    title: t("home.features.submissions.title"),
    description: t("home.features.submissions.description"),
    badge: {
      label: t("home.features.submissions.badge"),
      color: "success" as const,
    },
  },
];

const roadmapItems = [
  {
    icon: "i-heroicons-user-group",
    title: t("home.roadmap.teamFormation.title"),
    description: t("home.roadmap.teamFormation.description"),
    status: t("home.roadmap.planned"),
  },
  {
    icon: "i-heroicons-paper-airplane",
    title: t("home.roadmap.submissions.title"),
    description: t("home.roadmap.submissions.description"),
    status: t("home.roadmap.planned"),
  },
  {
    icon: "i-heroicons-trophy",
    title: t("home.roadmap.winnerElection.title"),
    description: t("home.roadmap.winnerElection.description"),
    status: t("home.roadmap.planned"),
  },
];
</script>

<template>
  <div>
    <!-- Hero Section -->
    <HomeHeroSection />

    <!-- About Section -->
    <HomeAboutSection />

    <!-- Features Section -->
    <HomeFeaturesSection
      :organizer-features="organizerFeatures"
      :participant-features="participantFeatures"
    />

    <!-- Roadmap -->
    <HomeRoadmapSection :items="roadmapItems" />

    <!-- Call to Action Section -->
    <HomeCtaSection />
  </div>
</template>
