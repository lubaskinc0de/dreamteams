<script setup lang="ts">
/**
 * Переиспользуемый компонент для отображения строки информации
 * с иконкой, лейблом и значением
 */

interface Props {
  icon?: string;
  label?: string;
  value: string;
  size?: 'sm' | 'md';
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
});
</script>

<template>
  <div class="flex items-center gap-2">
    <UIcon v-if="icon" :name="icon" :class="size === 'sm' ? 'size-4' : 'size-5'" />
    <span :class="size === 'sm' ? 'text-sm' : 'text-base'">
      <template v-if="label">{{ label }}: </template>{{ value }}
    </span>
  </div>
</template>
