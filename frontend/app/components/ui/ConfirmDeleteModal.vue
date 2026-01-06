<script setup lang="ts">
/**
 * Переиспользуемый компонент модального окна подтверждения удаления
 */

interface Props {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  isDeleting?: boolean;
}

interface Emits {
  'update:open': [value: boolean];
  'confirm': [];
}

const props = withDefaults(defineProps<Props>(), {
  confirmLabel: 'Delete',
  cancelLabel: 'Cancel',
  isDeleting: false,
});

const emit = defineEmits<Emits>();

const handleConfirm = () => {
  emit('confirm');
};

const handleCancel = () => {
  emit('update:open', false);
};
</script>

<template>
  <UModal
    :model-value="open"
    @update:model-value="emit('update:open', $event)"
    :title="title"
    :description="description"
    :ui="{ footer: 'justify-end' }"
  >
    <template #footer>
      <UButton
        color="neutral"
        variant="outline"
        :label="cancelLabel"
        @click="handleCancel"
        :disabled="isDeleting"
      />
      <UButton
        color="error"
        :label="confirmLabel"
        :loading="isDeleting"
        :disabled="isDeleting"
        @click="handleConfirm"
      />
    </template>
  </UModal>
</template>
