<script setup lang="ts">
import type { CompetitionModel } from '~/types/api';

/**
 * Компонент для отображения статуса соревнования (Архив / Открыта регистрация / и т.д.)
 */

interface Props {
  competition: CompetitionModel;
  size?: 'sm' | 'md' | 'lg';
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
});

const { t } = useI18n();
const { getRegistrationStatus, isArchived } = useCompetitionStatus();
</script>

<template>
  <UBadge
    v-if="isArchived(competition)"
    color="warning"
    variant="subtle"
    :size="size"
    :label="t('competition.detail.archivedBadge')"
  />
  <UBadge
    v-else
    :color="getRegistrationStatus(competition).color"
    variant="subtle"
    :size="size"
    :label="getRegistrationStatus(competition).label"
  />
</template>
