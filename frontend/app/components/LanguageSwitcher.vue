<script setup lang="ts">
import type { DropdownMenuItem } from "#ui/types";

/**
 * Language switcher component
 * Allows users to switch between available locales
 * Uses UDropdownMenu from Nuxt UI v4
 */
const { locale, locales, setLocale } = useI18n();

interface Props {
  variant?: "solid" | "outline" | "soft" | "ghost" | "link";
  color?:
    | "primary"
    | "secondary"
    | "success"
    | "info"
    | "warning"
    | "error"
    | "neutral";
  size?: "xs" | "sm" | "md" | "lg" | "xl";
}

const props = withDefaults(defineProps<Props>(), {
  variant: "ghost",
  color: "neutral",
  size: "md",
});

// Current locale display
const currentLocale = computed(() => {
  return locales.value.find((i) => i.code === locale.value);
});

// Menu items for language selection
const items = computed<DropdownMenuItem[]>(() => {
  return locales.value.map((loc) => ({
    label: loc.name || loc.code.toUpperCase(),
    icon: "i-heroicons-language",
    onSelect: async () => {
      await setLocale(loc.code as "ru" | "en");
      // Force reload to apply language changes everywhere
      window.location.reload();
    },
  }));
});
</script>

<template>
  <UDropdownMenu :items="items" :size="props.size">
    <UButton
      icon="i-heroicons-language"
      :variant="props.variant"
      :color="props.color"
      :size="props.size"
      trailing-icon="i-heroicons-chevron-down"
      :aria-label="`Current language: ${currentLocale?.name || 'Unknown'}`"
    >
      {{ currentLocale?.name || "RU" }}
    </UButton>
  </UDropdownMenu>
</template>
