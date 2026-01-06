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

// Setup infinite scroll
onMounted(() => {
  if (scrollArea.value?.$el) {
    useInfiniteScroll(scrollArea.value.$el, () => {
      emit('load-more');
    }, {
      distance: 200,
      canLoadMore: () => {
        return props.hasMore && !props.loading;
      }
    });
  }
});
</script>

<template>
  <div class="flex-1 relative">
    <UScrollArea
      ref="scrollArea"
      class="h-[calc(100vh-280px)]"
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
