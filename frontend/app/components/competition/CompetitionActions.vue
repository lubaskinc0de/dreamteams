<script setup lang="ts">
/**
 * Компонент с кнопками действий для соревнования
 */

interface Props {
  editLabel?: string;
  deleteLabel?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

interface Emits {
  'edit': [];
  'delete': [];
}

withDefaults(defineProps<Props>(), {
  editLabel: 'Edit',
  deleteLabel: 'Delete',
  size: 'lg',
});

const emit = defineEmits<Emits>();
</script>

<template>
  <div class="flex items-center gap-3">
    <UButton
      icon="i-heroicons-pencil"
      color="primary"
      :size="size"
      :label="editLabel"
      @click="emit('edit')"
    />
    <UButton
      icon="i-heroicons-trash"
      color="error"
      :size="size"
      variant="outline"
      :label="deleteLabel"
      @click="emit('delete')"
    />
  </div>
</template>
