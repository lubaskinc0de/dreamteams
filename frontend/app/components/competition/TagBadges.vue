<script setup lang="ts">
import type { CompetitionTag } from "~/types/api";

interface Props {
  tags: CompetitionTag[];
  size?: "sm" | "md" | "lg";
}

withDefaults(defineProps<Props>(), {
  size: "md",
});
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <UBadge
      v-for="tag in tags"
      :key="tag.id"
      variant="soft"
      :size="size"
      :label="tag.value"
    />
  </div>
</template>
