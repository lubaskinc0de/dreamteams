<script setup lang="ts">
/**
 * Scrollable list of competition cards with loading indicator
 */
import type { CompetitionModel } from '~/types/api';
import { useInfiniteScroll } from '@vueuse/core';

interface Props {
  competitions: CompetitionModel[];
  loading: boolean;
  hasMore: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits(['click', 'delete', 'load-more']);

const scrollArea = useTemplateRef('scrollArea');
const isScrollSetup = ref(false);

// Setup infinite scroll when scrollArea becomes available
watch(scrollArea, (newRef) => {
  if (newRef?.$el && !isScrollSetup.value) {
    useInfiniteScroll(newRef.$el, () => {
      emit('load-more');
    }, {
      distance: 200,
      canLoadMore: () => {
        return props.hasMore && !props.loading;
      }
    });
    isScrollSetup.value = true;
  }
}, { immediate: true });
</script>

<template>
  <div class="flex-1 min-w-0 relative flex flex-col overflow-hidden">
    <UScrollArea
      ref="scrollArea"
      class="flex-1 min-h-0"
      :ui="{ viewport: 'gap-4 p-1' }"
    >
      <CompetitionCard
        v-for="competition in competitions"
        :key="competition.id"
        :competition="competition"
        @click="emit('click', $event)"
        @delete="emit('delete', $event)"
      />
    </UScrollArea>

    <!-- Loading Indicator -->
    <UProgress
      v-if="loading"
      indeterminate
      size="xs"
      class="absolute top-0 inset-x-0 z-1"
      :ui="{ base: 'bg-default' }"
    />
  </div>
</template>
