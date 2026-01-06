<script setup lang="ts">
import type { Domain } from '~/types/api';

/**
 * Компонент для отображения списка доменов соревнования как бейджей
 */

interface Props {
  domains: Domain[];
  size?: 'sm' | 'md' | 'lg';
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
});

const { getDomainLabel } = useCompetitionFormatters();
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <UBadge
      v-for="domain in domains"
      :key="domain"
      variant="soft"
      :size="size"
      :label="getDomainLabel(domain)"
    />
  </div>
</template>
