<script setup lang="ts">
import type { TimelineItem } from "@nuxt/ui";
import type { Milestone } from "~/types/api";
import { extractMilestoneDescription } from "~/utils/milestone";

interface Props {
  milestones: Milestone[];
}

const props = defineProps<Props>();

const { t } = useI18n();
const { formatDateTime } = useCompetitionFormatters();

const timelineItems = computed<TimelineItem[]>(() =>
  props.milestones.map((m) => ({
    title: m.title,
    date: formatDateTime(m.timestamp),
    description: extractMilestoneDescription(m.description) ?? undefined,
    icon: "i-heroicons-flag",
  })),
);
</script>

<template>
  <UCard v-if="milestones.length > 0">
    <template #header>
      <h2 class="text-xl font-semibold">{{ t("competition.detail.milestones") }}</h2>
    </template>
    <UTimeline :items="timelineItems" color="primary" />
  </UCard>
</template>
