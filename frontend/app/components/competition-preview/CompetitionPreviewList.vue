<script setup lang="ts">
/**
 * Grid of competition preview cards.
 * Layout: 3 columns on lg+, 2 on sm+, 1 on mobile.
 * Pagination: infinite scroll on all breakpoints.
 */
import type { PreviewCompetitionModel } from "~/types/api";
import { useInfiniteScroll } from "@vueuse/core";

interface Props {
  competitions: PreviewCompetitionModel[];
  loading: boolean;
  hasMore: boolean;
  canRegister?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  canRegister: true,
});
const emit = defineEmits(["register", "load-more", "view-details"]);

const sentinelEl = useTemplateRef<HTMLElement>("sentinelEl");

onMounted(() => {
  useInfiniteScroll(
    window,
    () => emit("load-more"),
    {
      distance: 400,
      canLoadMore: () => props.hasMore && !props.loading,
    },
  );
});
</script>

<template>
  <div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
      <CompetitionPreviewCard
        v-for="competition in competitions"
        :key="competition.id"
        :competition="competition"
        :can-register="canRegister"
        @register="emit('register', $event)"
        @click="emit('view-details', $event)"
      />
    </div>

    <!-- Infinite scroll sentinel -->
    <div ref="sentinelEl" aria-hidden="true" />

    <!-- Loading indicator -->
    <div v-if="loading" class="flex justify-center py-8">
      <UProgress indeterminate size="xs" class="w-48" />
    </div>
  </div>
</template>
