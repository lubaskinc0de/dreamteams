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

/**
 * Возвращает иконку в зависимости от статуса соревнования
 */
const getStatusIcon = computed(() => {
  if (isArchived(props.competition)) {
    return 'i-heroicons-archive-box';
  }

  const status = getRegistrationStatus(props.competition);

  if (status.color === 'success') {
    // Регистрация открыта
    return 'i-heroicons-check-circle';
  } else if (status.color === 'warning') {
    // Регистрация еще не открыта
    return 'i-heroicons-clock';
  } else {
    // Регистрация закрыта
    return 'i-heroicons-x-circle';
  }
});
</script>

<template>
  <UBadge
    v-if="isArchived(competition)"
    color="warning"
    variant="subtle"
    :size="size"
    :label="t('competition.detail.archivedBadge')"
    :icon="getStatusIcon"
  />
  <UBadge
    v-else
    :color="getRegistrationStatus(competition).color"
    variant="subtle"
    :size="size"
    :label="getRegistrationStatus(competition).label"
    :icon="getStatusIcon"
  />
</template>
