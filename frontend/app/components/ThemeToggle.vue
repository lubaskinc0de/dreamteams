<script setup lang="ts">
interface Props {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

withDefaults(defineProps<Props>(), {
  size: 'md',
});
</script>

<template>
  <UColorModeSelect :size="size" />
</template>
